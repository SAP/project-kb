from abc import abstractmethod
import re
from typing import List, Set, Tuple


from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.nlp import extract_similar_words
from rules.helpers import (
    extract_commit_mentioned_in_linked_pages,
    extract_security_keywords,
)
from stats.execution import Counter, execution_statistics
from util.lsh import build_lsh_index, decode_minhash


rule_statistics = execution_statistics.sub_collection("rules")


class Rule:
    id = ""

    def __init__(self, relevance: int):
        self.message = ""
        self.relevance = relevance

    @abstractmethod
    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord) -> bool:
        pass

    def get_message(self):
        return self.message

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
                    candidate.add_match(rule.get_rule_as_tuple())
                    # candidate.annotations[rule.id] = rule.message
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

    id = "CVE_ID_IN_MESSAGE"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if advisory_record.vulnerability_id in candidate.cve_refs:
            self.message = f"The commit message mentions the vulnerability identifier {advisory_record.vulnerability_id}"
            return True
        return False


class ReferencesGhIssue(Rule):
    """Matches commits that refer to a GitHub issue in the commit message or title."""

    id = "GH_ISSUE_IN_MESSAGE"

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        if len(candidate.ghissue_refs) > 0:
            self.message = f"The commit message references the following GitHub issue/pr: {', '.join(candidate.ghissue_refs)}"
            return True
        return False


class ReferencesJiraIssue(Rule):
    """Matches commits that refer to a JIRA issue in the commit message or title."""

    id = "JIRA_ISSUE_IN_MESSAGE"

    def apply(
        self, candidate: Commit, _: AdvisoryRecord = None
    ):  # test to see if I can remove the advisory record from here
        if len(candidate.jira_refs) > 0:
            self.message = f"The commit message references the following Jira issue: {', '.join(candidate.jira_refs)}"
            return True
        return False


class ChangesRelevantFiles(Rule):
    """Matches commits that modify some file mentioned in the advisory text."""

    id = "CHANGES_RELEVANT_FILES"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        relevant_files = set(
            [
                file
                for file in candidate.changed_files
                for adv_path in advisory_record.paths
                if adv_path.casefold() in file.casefold()
                and len(adv_path)
                > 3  # TODO: when fixed extraction the >3 should be useless
            ]
        )
        if len(relevant_files) > 0:
            self.message = f"The commit changes the following relevant files: {', '.join(relevant_files)}"
            return True
        return False


class AdvKeywordsInMsg(Rule):
    """Matches commits whose message contain any of the keywords extracted from the advisory."""

    id = "ADV_KEYWORDS_IN_MESSAGE"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = set(
            extract_similar_words(advisory_record.keywords, candidate.message)
        )
        if len(matching_keywords) > 0:
            self.message = f"The commit message and the advisory share the following keywords: {', '.join(matching_keywords)}"
            return True
        return False


# TODO: with proper filename and msg search this could be deprecated ?
class AdvKeywordsInDiffs(Rule):
    """Matches commits whose diffs contain any of the keywords extracted from the advisory."""

    id = "ADV_KEYWORDS_IN_DIFFS"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        return False
        matching_keywords = set(
            extract_similar_words(advisory_record.keywords, candidate.diff)
        )
        return len(matching_keywords) > 0


class AdvKeywordsInFiles(Rule):
    """Matches commits that modify paths corresponding to a keyword extracted from the advisory."""

    id = "ADV_KEYWORDS_IN_FILES"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = set(
            [
                (p, token)
                for p in candidate.changed_files
                for token in advisory_record.keywords
                if token in p
            ]
        )
        if len(matching_keywords) > 0:
            self.message = f"The commit changes files whose name contains a keyword from the advisory: {','.join([f'{m[0]} ({m[1]})' for m in matching_keywords])}"
            return True
        return False


class SecurityKeywordsInMsg(Rule):
    """Matches commits whose message contains one or more security-related keywords."""

    id = "SEC_KEYWORDS_IN_MESSAGE"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord = None):
        matching_keywords = extract_security_keywords(candidate.message)
        if len(matching_keywords) > 0:
            self.message = f"The commit message contains the following security-related keywords: {', '.join(matching_keywords)}"
            return True
        return False


class CommitMentionedInAdvisory(Rule):
    """Matches commits that are linked in the advisory page."""

    id = "COMMIT_IN_ADVISORY"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_references = set(
            [
                ref
                for ref in advisory_record.references
                if candidate.commit_id[:8] in ref
            ]
        )
        if len(matching_references) > 0:
            self.message = (
                f"Commit mentioned in the advisory: {', '.join(matching_references)}"
            )
            return True
        return False


# TODO: refactor these rules to not scan multiple times the same commit
class CveIdInLinkedIssue(Rule):
    """Matches commits linked to an issue containing the CVE-ID."""

    id = "CVE_ID_IN_LINKED_ISSUE"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for id, content in candidate.ghissue_refs.items():
            if advisory_record.vulnerability_id in content:
                self.message = f"The issue (or pull request) {id} mentions the vulnerability id {advisory_record.vulnerability_id}"
                return True

        return False


class SecurityKeywordInLinkedGhIssue(Rule):
    """Matches commits linked to an issue containing one or more security-related keywords."""

    id = "SEC_KEYWORDS_IN_LINKED_GH"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord = None):
        for id, issue_content in candidate.ghissue_refs.items():

            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The linked issue/PR {id} contains the following security-related terms: {', '.join(matching_keywords)}"
                return True
        return False


class SecurityKeywordInLinkedJiraIssue(Rule):
    """Matches commits linked to a jira issue containing one or more security-related keywords."""

    id = "SEC_KEYWORDS_IN_LINKED_JIRA"

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.jira_refs.items():

            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The jira issue {id} contains the following security-related terms: {', '.join(matching_keywords)}"
                return True

        return False


class CrossReferencedJiraLink(Rule):
    """Matches commits whose message contains a jira issue which is also referenced by the advisory."""

    id = "CROSS_REFERENCED_JIRA_LINK"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = [
            id
            for id in candidate.jira_refs
            for url in advisory_record.references
            if id in url and "jira" in url
        ]
        if len(matches) > 0:
            self.message = f"The commit message and the advisory mention the same jira issue(s): {', '.join(matches)}"
            return True
        return False


class CrossReferencedGhLink(Rule):
    """Matches commits whose message contains a github issue/pr which is also referenced by the advisory."""

    id = "CROSS_REFERENCED_GH_LINK"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = [
            id
            for id in candidate.ghissue_refs
            for url in advisory_record.references
            if id in url and "github.com" in url
        ]
        if len(matches) > 0:
            self.message = f"The commit message and the advisory mention the same github issue/PR: {', '.join(matches)}"
            return True
        return False


class SmallCommit(Rule):
    """Matches small commits (i.e., they modify a small number of contiguous lines of code)."""

    id = "SMALL_COMMIT"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if candidate.hunk_count < 10:
            self.message = f"This commit modifies only {candidate.hunk_count} contiguous lines of code"
            return True
        return False


class CommitMentionedInReference(Rule):
    """Matches commits that are mentioned in any of the links contained in the advisory page."""

    id = "COMMIT_IN_REFERENCE"

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if extract_commit_mentioned_in_linked_pages(candidate, advisory_record):
            self.message = (
                "This commit is mentioned in one or more pages linked by the advisory"
            )

            return True
        return False


RULES: Set[Rule] = set(
    [
        CveIdInMessage(10),
        CommitMentionedInAdvisory(10),
        CrossReferencedJiraLink(9),
        CrossReferencedGhLink(9),
        CommitMentionedInReference(9),
        CveIdInLinkedIssue(9),
        ChangesRelevantFiles(9),
        AdvKeywordsInDiffs(8),
        AdvKeywordsInFiles(8),
        AdvKeywordsInMsg(5),
        SecurityKeywordsInMsg(5),
        SecurityKeywordInLinkedGhIssue(5),
        SecurityKeywordInLinkedJiraIssue(5),
        ReferencesGhIssue(2),
        ReferencesJiraIssue(2),
        SmallCommit(0),
    ]
)
