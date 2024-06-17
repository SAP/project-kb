import re
from abc import abstractmethod
from typing import Tuple

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from rules.helpers import extract_security_keywords
from rules.rule import Rule
from util.lsh import decode_minhash


class NLPRule(Rule):
    lsh_index = None

    def __init__(self, id: str, relevance: int):
        super().__init__(id, relevance)

    @abstractmethod
    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord) -> bool:
        pass

    def get_message(self):
        return super().get_message()

    def as_dict(self):
        return super().as_dict()

    def get_rule_as_tuple(self) -> Tuple[str, str, int]:
        return super().get_rule_as_tuple()


# TODO: This could include issues, PRs, etc.
class VulnIdInMessage(NLPRule):
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
class GHSecurityAdvInMessage(NLPRule):
    """Matches commits that refer to a GHSA in the commit message."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        if bool(re.search(r"GHSA(?:-[a-z0-9]{4}){3}", candidate.message)):
            return False
            # if advisory_record.cve_id in page_content:
            #     self.message = "The commit message mentions the GHSA corresponding to the CVE ID"
            #     return True
        return False


class ReferencesGhIssue(NLPRule):
    """Matches commits that refer to a GitHub issue in the commit message or title."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        if len(candidate.ghissue_refs) > 0:
            self.message = f"The commit message references some github issue: {', '.join(candidate.ghissue_refs)}"
            return True
        return False


class ReferencesBug(NLPRule):
    """Matches commits that refer to a bug tracking ticket in the commit message or title."""

    def apply(
        self, candidate: Commit, _: AdvisoryRecord = None
    ):  # test to see if I can remove the advisory record from here
        if len(candidate.jira_refs) > 0:
            self.message = f"The commit message references some bug tracking ticket: {', '.join(candidate.jira_refs)}"
            return True
        return False


class ChangesRelevantFiles(NLPRule):
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


class AdvKeywordsInMsg(NLPRule):
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
class ChangesRelevantCode(NLPRule):
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


class AdvKeywordsInFiles(NLPRule):
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


class SecurityKeywordsInMsg(NLPRule):
    """Matches commits whose message contains one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        matching_keywords = extract_security_keywords(candidate.message)
        if len(matching_keywords) > 0:
            self.message = f"The commit message contains some security-related keywords: {', '.join(matching_keywords)}"
            return True
        return False


class CommitMentionedInAdv(NLPRule):
    """Matches commits that are linked in the advisory page."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for ref, src in advisory_record.references.items():
            if candidate.commit_id[:8] in ref and len(src) == 0:
                self.message = "The commit is mentioned in the advisory page"
                return True
        return False


class TwinMentionedInAdv(NLPRule):
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
class VulnIdInLinkedIssue(NLPRule):
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


class SecurityKeywordInLinkedGhIssue(NLPRule):
    """Matches commits linked to an issue containing one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.ghissue_refs.items():
            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The github issue {id} contains some security-related terms: {', '.join(matching_keywords)}"
                return True
        return False


class SecurityKeywordInLinkedBug(NLPRule):
    """Matches commits linked to a bug tracking ticket containing one or more security-related keywords."""

    def apply(self, candidate: Commit, _: AdvisoryRecord = None):
        for id, issue_content in candidate.jira_refs.items():
            matching_keywords = extract_security_keywords(issue_content)

            if len(matching_keywords) > 0:
                self.message = f"The bug tracking ticket {id} contains some security-related terms: {', '.join(matching_keywords)}"
                return True

        return False


class CrossReferencedBug(NLPRule):
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


class CrossReferencedGh(NLPRule):
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


class CommitMentionedInReference(NLPRule):
    """Matches commits that are mentioned in any of the links contained in the advisory page."""

    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord):
        for ref, n in advisory_record.references.items():
            if candidate.commit_id[:8] in ref:
                self.message = f"This commit is mentioned {n} times in the references."
                return True
        return False


class CommitHasTwins(NLPRule):
    def apply(self, candidate: Commit, _: AdvisoryRecord) -> bool:
        if not NLPRule.lsh_index.is_empty() and not bool(
            re.match(r"Merge", candidate.message, flags=re.IGNORECASE)
        ):
            twin_list = NLPRule.lsh_index.query(decode_minhash(candidate.minhash))
            # twin_list.remove(candidate.commit_id)
            candidate.twins = [
                ["no-tag", twin] for twin in twin_list if twin != candidate.commit_id
            ]
        # self.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))
        if len(candidate.twins) > 0:
            self.message = "This commit has one or more twins."
            return True
        return False


class RelevantWordsInMessage(NLPRule):
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
