import re
from abc import abstractmethod
from typing import List, Tuple

import requests

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, apply_ranking
from llm.llm_service import LLMService
from rules.helpers import extract_security_keywords
from stats.execution import Counter, execution_statistics
from util.lsh import build_lsh_index, decode_minhash

NUM_COMMITS_PHASE_2 = (
    10  # Determines how many candidates the second rule phase is applied to
)


rule_statistics = execution_statistics.sub_collection("rules")


class Rule:
    lsh_index = None
    llm_service: LLMService = None

    def __init__(self, id: str, relevance: int):
        self.id = id
        self.relevance = relevance
        self.message = ""

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

    def get_id(self):
        return self.id


def apply_rules(
    candidates: List[Commit],
    advisory_record: AdvisoryRecord,
    backend_address: str,
    enabled_rules: List[str] = [],
) -> List[Commit]:
    """Applies the selected set of rules and returns the ranked list of commits."""

    phase_1_rules = [rule for rule in RULES_PHASE_1 if rule.get_id() in enabled_rules]
    phase_2_rules = [rule for rule in RULES_PHASE_2 if rule.get_id() in enabled_rules]

    if phase_2_rules:
        Rule.llm_service = LLMService()

    rule_statistics.collect(
        "active", len(phase_1_rules) + len(phase_2_rules), unit="rules"
    )

    Rule.lsh_index = build_lsh_index()
    for candidate in candidates:
        Rule.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for rule in phase_1_rules:
                if rule.apply(candidate, advisory_record):
                    counter.increment("matches")
                    candidate.add_match(rule.as_dict())
            candidate.compute_relevance()

        candidates = apply_ranking(candidates)

        for candidate in candidates[:NUM_COMMITS_PHASE_2]:
            for rule in phase_2_rules:
                if rule.apply(candidate, backend_address):
                    counter.increment("matches")
                    candidate.add_match(rule.as_dict())
            candidate.compute_relevance()

    return apply_ranking(candidates)


# TODO: This could include issues, PRs, etc.
class VulnIdInMessage(Rule):
    """Matches commits that refer to the Vuln-ID in the commit message."""  # Check if works for the title or comments

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if (
            advisory_record.cve_id in candidate.cve_refs
            and len(candidate.cve_refs) == 1
        ):
            self.message = "The commit message mentions the vulnerability ID"
            return True
        return False


# TODO: This could include issues, PRs and commits
class GHSecurityAdvInMessage(Rule):
    """Matches commits that refer to a GHSA in the commit message."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if bool(re.search(r"GHSA(?:-[a-z0-9]{4}){3}", candidate.message)):
            return False
            # if advisory_record.cve_id in page_content:
            #     self.message = "The commit message mentions the GHSA corresponding to the CVE ID"
            #     return True
        return False


class ReferencesGhIssue(Rule):
    """Matches commits that refer to a GitHub issue in the commit message or title."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        if len(candidate.ghissue_refs) > 0:
            self.message = f"The commit message references some github issue: {', '.join(candidate.ghissue_refs)}"
            return True
        return False


class ReferencesBug(Rule):
    """Matches commits that refer to a bug tracking ticket in the commit message or title."""

    def apply(
        self, candidate: Commit, _: AdvisoryRecord = None
    ):  # test to see if I can remove the advisory record from here
        if len(candidate.jira_refs) > 0:
            self.message = f"The commit message references some bug tracking ticket: {', '.join(candidate.jira_refs)}"
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
                and adv_file.casefold() not in candidate.repository.split("/")
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
        # regex = r"[^a-z0-9]({})[^a-z0-9]".format("|".join(advisory_record.keywords))
        # matching_keywords = set(
        #     [
        #         m.group(1)
        #         for m in re.finditer(regex, candidate.message, flags=re.IGNORECASE)
        #         if m.group(1).casefold() not in candidate.repository
        #     ]
        # )
        matching_keywords = set(
            [
                token
                for token in advisory_record.keywords
                if token in candidate.message.casefold()
                and token not in candidate.repository
            ]
        )
        # matching_keywords = find_similar_words(
        #     advisory_record.keywords, candidate.message, candidate.repository
        # )

        if len(matching_keywords) > 0:
            self.message = f"The commit message and the advisory description contain the following keywords: {', '.join(matching_keywords)}"
            return True
        return False


# TODO: Test it
class ChangesRelevantCode(Rule):
    """Matches commits whose diffs contain any of the relevant files/methods extracted from the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = []
        for word in advisory_record.files:
            for diffline in candidate.diff:
                if (
                    word not in matching_keywords
                    and word in diffline
                    and word.casefold() not in candidate.repository.split("/")
                    and "diff --git" not in diffline
                    and "---" not in diffline
                    and "+++" not in diffline
                ):
                    matching_keywords.append(word)
                elif word in matching_keywords:
                    break
        if len(matching_keywords) > 0:
            self.message = f"The commit modifies code containing relevant filename or methods: {', '.join(matching_keywords)}"
            return True
        return False


class AdvKeywordsInFiles(Rule):
    """Matches commits that modify paths corresponding to a keyword extracted from the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_keywords = set(
            [
                (p, token)
                for p in candidate.changed_files
                for token in advisory_record.keywords
                if token.casefold() in p.casefold()
                and token.casefold() not in candidate.repository
            ]
        )

        if len(matching_keywords) > 0:
            self.message = f"An advisory keyword is contained in the changed files: {', '.join(set([t for _, t in matching_keywords]))}"
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
        for ref, src in advisory_record.references.items():
            if candidate.commit_id[:8] in ref and len(src) == 0:
                self.message = "The commit is mentioned in the advisory page"
                return True
        return False


class TwinMentionedInAdv(Rule):
    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for ref in advisory_record.references:
            for twin in candidate.twins:
                if twin[1][:8] in ref:
                    self.message = (
                        "A twin of this commit is mentioned in the advisory page"
                    )
                    return True
        return False


# TODO: refactor these rules to not scan multiple times the same commit
class VulnIdInLinkedIssue(Rule):
    """Matches commits linked to an issue containing the Vuln-ID."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for id, content in candidate.ghissue_refs.items():
            if (
                advisory_record.cve_id in content
                and len(re.findall(r"CVE-\d{4}-\d{4,8}", content)) == 1
            ):
                self.message = f"Issue {id} linked to the commit mentions the Vuln ID. "
                return True

        for id, content in candidate.jira_refs.items():
            if (
                advisory_record.cve_id in content
                and len(re.findall(r"CVE-\d{4}-\d{4,8}", content)) == 1
            ):
                self.message = f"The bug tracking ticket {id} linked to the commit mentions the Vuln ID"

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


class SecurityKeywordInLinkedBug(Rule):
    """Matches commits linked to a bug tracking ticket containing one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.jira_refs.items():
            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The bug tracking ticket {id} contains some security-related terms: {', '.join(matching_keywords)}"
                return True

        return False


class CrossReferencedBug(Rule):
    """Matches commits whose message contains a bug tracking ticket which is also referenced by the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = set(
            [
                id
                for id in candidate.jira_refs
                for url in advisory_record.references
                if id in url and "jira" in url
            ]
        )
        if len(matches) > 0:
            self.message = f"The commit and the advisory (including referenced pages) mention the same bug tracking ticket: {', '.join(matches)}"
            return True
        return False


class CrossReferencedGh(Rule):
    """Matches commits whose message contains a github issue/pr which is also referenced by the advisory."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matches = [
            id
            for id in candidate.ghissue_refs.keys()
            for url in advisory_record.references.keys()
            if id in url.split("/") and url.startswith(candidate.repository)
        ]

        if len(matches) > 0:
            self.message = f"The commit and the advisory (including referenced pages) mention the same github issue: {', '.join(matches)}"
            return True
        return False


class CommitMentionedInReference(Rule):
    """Matches commits that are mentioned in any of the links contained in the advisory page."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for ref, n in advisory_record.references.items():
            if candidate.commit_id[:8] in ref:
                self.message = f"This commit is mentioned {n} times in the references."
                return True
        return False


class CommitHasTwins(Rule):
    def apply(self, candidate: Commit, _: AdvisoryRecord) -> bool:
        if not Rule.lsh_index.is_empty() and not bool(
            re.match(r"Merge", candidate.message, flags=re.IGNORECASE)
        ):
            twin_list = Rule.lsh_index.query(decode_minhash(candidate.minhash))
            # twin_list.remove(candidate.commit_id)
            candidate.twins = [
                ["no-tag", twin] for twin in twin_list if twin != candidate.commit_id
            ]
        # self.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))
        if len(candidate.twins) > 0:
            self.message = "This commit has one or more twins."
            return True
        return False


class RelevantWordsInMessage(Rule):
    """Matches commits whose message contains one or more relevant words."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        matching_words = set(
            [
                token
                for token in advisory_record.files
                if token in candidate.message.split()
            ]
        )
        # [
        #     file
        #     for file in candidate.changed_files
        #     for adv_file in advisory_record.files
        #     if adv_file.casefold() in file.casefold()
        #     and adv_file.casefold() not in candidate.repository.split("/")
        #     and len(adv_file)
        #     > 3  # TODO: when fixed extraction the >3 should be useless
        # ]
        if len(matching_words) > 0:
            self.message = f"The commit message contains some relevant words: {', '.join(set(matching_words))}"
            return True
        return False


class CommitIsSecurityRelevant(Rule):
    """Matches commits that are deemed security relevant by the commit classification service."""

    def apply(
        self,
        candidate: Commit,
        backend_address: str,
    ) -> bool:

        # Check if this commit is already in the database
        try:
            r = requests.get(
                f"{backend_address}/commits/{candidate.repository}",
                params={"commit_id": candidate.commit_id},
                timeout=10
            )
            r.raise_for_status()
            commit_data = r.json()[0]

            is_security_relevant = commit_data.get('security_relevant')
            if is_security_relevant is not None:
                candidate.security_relevant = is_security_relevant
                return is_security_relevant

            candidate.security_relevant = LLMService().classify_commit(
                candidate.diff, candidate.repository, candidate.message
            )

            update_response = requests.post(
                backend_address + "/commits/",
                json=[candidate.to_dict()],
                headers={"content-type": "application/json"},
            )
            update_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            print(f"Error communicating with backend: {error_type} - {str(e)}")


RULES_PHASE_1: List[Rule] = [
    VulnIdInMessage("VULN_ID_IN_MESSAGE", 64),
    # CommitMentionedInAdv("COMMIT_IN_ADVISORY", 64),
    CrossReferencedBug("XREF_BUG", 32),
    CrossReferencedGh("XREF_GH", 32),
    CommitMentionedInReference("COMMIT_IN_REFERENCE", 64),
    VulnIdInLinkedIssue("VULN_ID_IN_LINKED_ISSUE", 32),
    ChangesRelevantFiles("CHANGES_RELEVANT_FILES", 8),
    ChangesRelevantCode("CHANGES_RELEVANT_CODE", 8),
    RelevantWordsInMessage("RELEVANT_WORDS_IN_MESSAGE", 8),
    AdvKeywordsInFiles("ADV_KEYWORDS_IN_FILES", 4),
    AdvKeywordsInMsg("ADV_KEYWORDS_IN_MSG", 4),
    SecurityKeywordsInMsg("SEC_KEYWORDS_IN_MESSAGE", 4),
    SecurityKeywordInLinkedGhIssue("SEC_KEYWORDS_IN_LINKED_GH", 4),
    SecurityKeywordInLinkedBug("SEC_KEYWORDS_IN_LINKED_BUG", 4),
    ReferencesGhIssue("GITHUB_ISSUE_IN_MESSAGE", 2),
    ReferencesBug("BUG_IN_MESSAGE", 2),
    CommitHasTwins("COMMIT_HAS_TWINS", 2),
]

RULES_PHASE_2: List[Rule] = [
    CommitIsSecurityRelevant("COMMIT_IS_SECURITY_RELEVANT", 32)
]
