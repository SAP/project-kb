from abc import abstractmethod
from typing import List, Tuple

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.nlp import find_similar_words
from rules.helpers import (
    extract_commit_mentioned_in_linked_pages,
    extract_security_keywords,
)
from stats.execution import Counter, execution_statistics
from util.lsh import build_lsh_index, decode_minhash

rule_statistics = execution_statistics.sub_collection("rules")


class Rule:
    lsh_index = build_lsh_index()

    def __init__(self, id: str, relevance: int):
        self.id = id
        self.message = ""
        self.relevance = relevance

    @abstractmethod
    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord) -> bool:
        pass

    def get_message(self):
        return self.message

    def as_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "relevance": self.relevance,
        }

    def get_rule_as_tuple(self) -> Tuple[str, str, int]:
        return (self.id, self.message, self.relevance)


def apply_rules(
    candidates: List[Commit],
    advisory_record: AdvisoryRecord,
    rules=["ALL"],
) -> List[Commit]:

    enabled_rules = get_enabled_rules(rules)

    rule_statistics.collect("active", len(enabled_rules), unit="rules")

    for candidate in candidates:
        Rule.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for rule in enabled_rules:
                if rule.apply(candidate, advisory_record):
                    counter.increment("matches")
                    candidate.add_match(rule.as_dict())
            candidate.compute_relevance()

    return candidates


def get_enabled_rules(rules: List[str]) -> List[Rule]:

    return RULES
    enabled_rules = []

    if "ALL" in rules:
        enabled_rules = RULES

    for r in rules:
        if r == "ALL":
            continue
        if r[0] != "-":
            enabled_rules.append(RULES.pop)
        elif r[0] == "-":
            rule_to_exclude = r[1:]
            if rule_to_exclude in enabled_rules:
                del enabled_rules[rule_to_exclude]

    return enabled_rules


class CveIdInMessage(Rule):
    """Matches commits that refer to the CVE-ID in the commit message."""  # Check if works for the title or comments

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if advisory_record.cve_id in candidate.cve_refs:
            self.message = "The commit message mentions the CVE ID"
            return True
        return False


class ReferencesGhIssue(Rule):
    """Matches commits that refer to a GitHub issue in the commit message or title."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        if len(candidate.ghissue_refs) > 0:
            self.message = f"The commit message references some github issue: {', '.join(candidate.ghissue_refs)}"
            return True
        return False


class ReferencesJiraIssue(Rule):
    """Matches commits that refer to a JIRA issue in the commit message or title."""

    def apply(
        self, candidate: Commit, _: AdvisoryRecord = None
    ):  # test to see if I can remove the advisory record from here
        if len(candidate.jira_refs) > 0:
            self.message = f"The commit message references some jira issue: {', '.join(candidate.jira_refs)}"
            return True
        return False


class ChangesRelevantFiles(Rule):
    """Matches commits that modify some file mentioned in the advisory text."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        relevant_files = set(
            [
                file
                for file in candidate.changed_files
                for adv_file in advisory_record.files
                if adv_file.casefold() in file.casefold()
                and adv_file.casefold() not in candidate.repository
                and len(adv_file)
                > 3  # TODO: when fixed extraction the >3 should be useless
            ]
        )
        if len(relevant_files) > 0:
            self.message = (
                f"The commit changes some relevant files: {', '.join(relevant_files)}"
            )
            return True
        return False


class AdvKeywordsInMsg(Rule):
    """Matches commits whose message contain any of the keywords extracted from the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = find_similar_words(
            advisory_record.keywords, candidate.message, candidate.repository
        )

        if len(matching_keywords) > 0:
            self.message = f"The commit and the advisory both contain the following keywords: {', '.join(matching_keywords)}"
            return True
        return False


# TODO: with proper filename and msg search this could be deprecated ?
class AdvKeywordsInDiffs(Rule):
    """Matches commits whose diffs contain any of the keywords extracted from the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        return False
        matching_keywords = find_similar_words(advisory_record.keywords, candidate.diff)

        return len(matching_keywords) > 0


class AdvKeywordsInFiles(Rule):
    """Matches commits that modify paths corresponding to a keyword extracted from the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = set(
            [
                (p, token)
                for p in candidate.changed_files
                for token in advisory_record.keywords
                if token in p and token not in candidate.repository
            ]
        )
        if len(matching_keywords) > 0:
            self.message = f"An advisory keyword is contained in the changed files: {', '.join([p for p, _ in matching_keywords])}"
            return True
        return False


class SecurityKeywordsInMsg(Rule):
    """Matches commits whose message contains one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        matching_keywords = extract_security_keywords(candidate.message)
        if len(matching_keywords) > 0:
            self.message = f"The commit message contains some security-related keywords: {', '.join(matching_keywords)}"
            return True
        return False


class CommitMentionedInAdv(Rule):
    """Matches commits that are linked in the advisory page."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_references = set(
            [
                ref
                for ref in advisory_record.references
                if candidate.commit_id[:8] in ref
            ]
        )
        if len(matching_references) > 0:
            self.message = "The advisory mentions the commit directly"  #: {', '.join(matching_references)}"
            return True
        return False


# TODO: refactor these rules to not scan multiple times the same commit
class CveIdInLinkedIssue(Rule):
    """Matches commits linked to an issue containing the CVE-ID."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for id, content in candidate.ghissue_refs.items():
            if advisory_record.cve_id in content:
                self.message = f"The issue {id} mentions the CVE ID"
                return True

        return False


class SecurityKeywordInLinkedGhIssue(Rule):
    """Matches commits linked to an issue containing one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.ghissue_refs.items():

            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The github issue {id} contains some security-related terms: {', '.join(matching_keywords)}"
                return True
        return False


class SecurityKeywordInLinkedJiraIssue(Rule):
    """Matches commits linked to a jira issue containing one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.jira_refs.items():

            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The jira issue {id} contains some security-related terms: {', '.join(matching_keywords)}"
                return True

        return False


class CrossReferencedJiraLink(Rule):
    """Matches commits whose message contains a jira issue which is also referenced by the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = [
            id
            for id in candidate.jira_refs
            for url in advisory_record.references
            if id in url and "jira" in url
        ]
        if len(matches) > 0:
            self.message = f"The commit and the advisory mention the same jira issue(s): {', '.join(matches)}"
            return True
        return False


class CrossReferencedGhLink(Rule):
    """Matches commits whose message contains a github issue/pr which is also referenced by the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = [
            id
            for id in candidate.ghissue_refs
            for url in advisory_record.references
            if id in url and "github.com" in url
        ]
        if len(matches) > 0:
            self.message = f"The commit and the advisory mention the same github issue(s): {', '.join(matches)}"
            return True
        return False


class SmallCommit(Rule):
    """Matches small commits (i.e., they modify a small number of contiguous lines of code)."""

    def apply(self, candidate: Commit, _: AdvisoryRecord):
        return False
        if candidate.get_hunks() < 10:  # 10
            self.message = (
                f"This commit modifies only {candidate.hunks} contiguous lines of code"
            )
            return True
        return False


# TODO: implement properly
class CommitMentionedInReference(Rule):
    """Matches commits that are mentioned in any of the links contained in the advisory page."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if extract_commit_mentioned_in_linked_pages(candidate, advisory_record):
            self.message = "A page linked in the advisory mentions this commit"

            return True
        return False


class CommitHasTwins(Rule):
    def apply(self, candidate: Commit, _: AdvisoryRecord) -> bool:
        if not Rule.lsh_index.is_empty():
            # TODO: the twin search must be done at the beginning, in the raw commits

            candidate.twins = Rule.lsh_index.query(decode_minhash(candidate.minhash))
            candidate.twins.remove(candidate.commit_id)
        # self.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))
        if len(candidate.twins) > 0:
            self.message = (
                f"This commit has one or more twins: {', '.join(candidate.twins)}"
            )
            return True
        return False


RULES = [
    CveIdInMessage("CVE_ID_IN_MESSAGE", 20),
    CommitMentionedInAdv("COMMIT_IN_ADVISORY", 20),
    CrossReferencedJiraLink("CROSS_REFERENCED_JIRA_LINK", 20),
    CrossReferencedGhLink("CROSS_REFERENCED_GH_LINK", 20),
    CommitMentionedInReference("COMMIT_IN_REFERENCE", 9),
    CveIdInLinkedIssue("CVE_ID_IN_LINKED_ISSUE", 9),
    ChangesRelevantFiles("CHANGES_RELEVANT_FILES", 9),
    AdvKeywordsInDiffs("ADV_KEYWORDS_IN_DIFFS", 5),
    AdvKeywordsInFiles("ADV_KEYWORDS_IN_FILES", 5),
    AdvKeywordsInMsg("ADV_KEYWORDS_IN_MSG", 5),
    SecurityKeywordsInMsg("SEC_KEYWORDS_IN_MESSAGE", 5),
    SecurityKeywordInLinkedGhIssue("SEC_KEYWORDS_IN_LINKED_GH", 5),
    SecurityKeywordInLinkedJiraIssue("SEC_KEYWORDS_IN_LINKED_JIRA", 5),
    ReferencesGhIssue("GITHUB_ISSUE_IN_MESSAGE", 2),
    ReferencesJiraIssue("JIRA_ISSUE_IN_MESSAGE", 2),
    SmallCommit("SMALL_COMMIT", 0),
    CommitHasTwins("COMMIT_HAS_TWINS", 5),
]
