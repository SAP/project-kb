from typing import Any, Callable, Dict, List, Tuple
from unicodedata import name

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from stats.execution import Counter, execution_statistics

from rules.helpers import (
    extract_commit_mentioned_in_linked_pages,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
)

SEC_KEYWORDS = [
    "vuln",
    "exploit",
    "attack",
    "secur",
    "xxe",
    "xss",
    "dos",
    "insecur",
    "inject",
    "unsafe",
    "patch",
    "remote execution",
    "malicious",
    " rce ",  # standalone RCE is a thing
]


class Rule:
    def __init__(self, rule_fun: Callable, relevance: int):
        self.rule_fun = rule_fun
        self.relevance = relevance

    def apply(
        self, candidate: Commit, advisory_record: AdvisoryRecord
    ) -> Tuple[str, int]:
        return self.rule_fun(candidate, advisory_record), self.relevance

    def __repr__(self):
        return f"Rule({self.rule_id}, {self.relevance})"


"""
QUICK GUIDE: HOW TO IMPLEMENT A NEW RULE

1. Start by adding an entry to the RULES dictionary (bottom of this file).
   Pick a clear rule id (all capitals, underscore separated) and a rule function
   (naming convention: "apply_rule_....")

2. Implement the rule function, which MUST take as input a Commit
   and an AdvisoryRecord and must return either None, if the rule did not match,
   or a string explaining the match that was found.

3. Do not forget to write a short comment at the beginning of the function explaining
   what the rule is about.

IMPORTANT: you are not supposed to change the content of function apply_rules.
"""

rule_statistics = execution_statistics.sub_collection("rules")


def apply_rules(
    candidates: List[Commit],
    advisory_record: AdvisoryRecord,
    rules=["ALL"],
) -> List[Commit]:
    """
    This applies a set of hand-crafted rules and returns a dict in the following form:

    commits_ruled[candidate] = ["explanation"]

    where 'explanation' describes the rule that matched for that candidate
    """

    enabled_rules = get_enabled_rules(rules)

    rule_statistics.collect("active", len(enabled_rules), unit="rules")

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for id, rule in enabled_rules.items():
                result, relevance = rule.apply(candidate, advisory_record)
                if result:
                    counter.increment("matches")
                    candidate.annotations[id] = result
                    candidate.relevance += relevance
    return candidates


def get_enabled_rules(rules: List[str]) -> Dict[str, Rule]:
    enabled_rules = dict()

    if "ALL" in rules:
        enabled_rules = RULES  # RULES_REGISTRY

    for r in rules:
        if r == "ALL":
            continue
        if r[0] != "-":
            enabled_rules[r] = RULES[r]
        elif r[0] == "-":
            rule_to_exclude = r[1:]
            if rule_to_exclude in enabled_rules:
                del enabled_rules[rule_to_exclude]

    return enabled_rules


def apply_rule_cve_id_in_msg(candidate: Commit, advisory_record: AdvisoryRecord) -> str:
    """Matches commits that refer to the CVE-ID in the commit message."""  # Check if works for the title or comments

    explanation_template = (
        "The commit message mentions the vulnerability identifier '{}'"
    )

    references_vuln_id = extract_references_vuln_id(candidate, advisory_record)
    if references_vuln_id:
        return explanation_template.format(advisory_record.vulnerability_id)
    return None


def apply_rule_references_ghissue(candidate: Commit, _) -> str:
    """Matches commits that refer to a GitHub issue in the commit message or title."""  # Check if works for the title or comments
    explanation_template = (
        "The commit message refers to the following GitHub issues: '{}'"
    )

    if len(candidate.ghissue_refs):
        return explanation_template.format(", ".join(candidate.ghissue_refs))
    return None


def apply_rule_references_jira_issue(candidate: Commit, _) -> str:
    """Matches commits that refer to a JIRA issue in the commit message or title."""  # Check if works for the title, comments
    explanation_template = "The commit message refers to the following Jira issues: {}"

    if len(candidate.jira_refs):
        return explanation_template.format(", ".join(candidate.jira_refs))

    return None


def apply_rule_changes_relevant_path(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits that touch some file that is mentioned
    in the text of the advisory.
    """
    explanation_template = "This commit touches the following relevant paths: {}"

    relevant_paths = set(
        [
            path
            for path in candidate.changed_files
            for adv_path in advisory_record.paths
            if adv_path in path
        ]
    )

    if len(relevant_paths):
        return explanation_template.format(", ".join(relevant_paths))

    return None


def apply_rule_adv_keywords_in_msg(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits whose message contain any of the special "code tokens" extracted from the advisory."""
    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in advisory_record.keywords if kw in candidate.message]
    )

    if len(matching_keywords):
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_adv_keywords_in_diff(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits whose diff contain any of the special "code tokens" extracted from the advisory."""

    # FIXME: this is hardcoded, read it from an "config" object passed to the rule function
    skip_tokens = ["IO"]

    explanation_template = "The commit diff includes the following keywords: {}"

    matching_keywords = set(
        [
            kw
            for kw in advisory_record.keywords
            for diff_line in candidate.diff
            if kw in diff_line and kw not in skip_tokens
        ]
    )

    if len(matching_keywords):
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_security_keyword_in_msg(candidate: Commit, _) -> str:
    """Matches commits whose message contains one or more "security-related" keywords."""
    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in SEC_KEYWORDS if kw in candidate.message.lower()]
    )

    if len(matching_keywords):
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_adv_keywords_in_paths(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits that modify paths corresponding to a code token extracted from the advisory."""
    explanation_template = "The commit modifies the following paths: {}"

    matches = set(
        [
            (p, token)
            for p in candidate.changed_files
            for token in advisory_record.keywords
            if token in p
        ]
    )
    if len(matches):
        explained_matches = [f"{m[0]} ({m[1]})" for m in matches]
        # for m in matches:
        #     explained_matches.append(f"{m[0]} ({m[1]})") for m in matches
        return explanation_template.format(", ".join(explained_matches))

    return None


def apply_rule_commit_mentioned_in_adv(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits that are linked in the advisory page."""
    explanation_template = (
        "One or more links to this commit appear in the advisory page: ({})"
    )
    commit_references = extract_referred_to_by_nvd(candidate, advisory_record)

    if len(commit_references):
        return explanation_template.format(", ".join(commit_references))

    return None


# Is this working?
def apply_rule_commit_mentioned_in_reference(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits that are mentioned in the links contained in the advisory page."""
    explanation_template = "This commit is mentioned in one or more referenced pages"

    count = extract_commit_mentioned_in_linked_pages(candidate, advisory_record)

    if count:
        return explanation_template

    return None


def apply_rule_vuln_mentioned_in_linked_issue(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits linked to an issue containing the CVE-ID."""

    explanation_template = (
        "The issue (or pull request) {} mentions the vulnerability id {}"
    )

    for ref, page_content in candidate.ghissue_refs.items():
        if not page_content:
            continue

        if advisory_record.vulnerability_id in page_content:

            return explanation_template.format(ref, advisory_record.vulnerability_id)

    return None


def apply_rule_security_keyword_in_linked_issue(candidate: Commit, _) -> str:
    """Matches commits linked to an issue containing one or more "security-related" keywords."""
    explanation_template = (
        "The issue (or pull request) {} contains security-related terms: {}"
    )

    for ref, page_content in candidate.ghissue_refs.items():

        if not page_content:
            continue

        matching_keywords = set(
            [kw for kw in SEC_KEYWORDS if kw in page_content.lower()]
        )
        if len(matching_keywords):
            return explanation_template.format(ref, ", ".join(matching_keywords))

    return None


def apply_rule_jira_issue_in_commit_msg_and_adv(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """Matches commits whose message contains a JIRA issue ID and the advisory mentions the same JIRA issue."""
    explanation_template = "The issue(s) {} (mentioned in the commit message) is referenced by the advisory"

    matches = [
        (i, j)
        for i in candidate.jira_refs
        for j in advisory_record.references
        if i in j
    ]
    if len(matches):
        ticket_ids = [id for (id, _) in matches]
        return explanation_template.format(", ".join(ticket_ids))

    return None


def apply_rule_small_commit(candidate: Commit, advisory_record: AdvisoryRecord) -> str:
    """Matches small commits (i.e., they modify a small number of contiguous lines of code)."""
    MAX_HUNKS = 10
    explanation_template = (
        "This commit modifies only {} hunks (groups of contiguous lines of code)"
    )

    if candidate.hunk_count <= MAX_HUNKS:
        return explanation_template.format(candidate.hunk_count)

    return None


RULES = {
    "CVE_ID_IN_COMMIT_MSG": Rule(apply_rule_cve_id_in_msg, 10),
    "TOKENS_IN_DIFF": Rule(apply_rule_adv_keywords_in_diff, 5),
    "TOKENS_IN_COMMIT_MSG": Rule(apply_rule_adv_keywords_in_msg, 10),
    "TOKENS_IN_MODIFIED_PATHS": Rule(apply_rule_adv_keywords_in_paths, 10),
    "SEC_KEYWORD_IN_COMMIT_MSG": Rule(apply_rule_security_keyword_in_msg, 5),
    "GH_ISSUE_IN_COMMIT_MSG": Rule(apply_rule_references_ghissue, 3),
    "JIRA_ISSUE_IN_COMMIT_MSG": Rule(apply_rule_references_jira_issue, 3),
    "CH_REL_PATH": Rule(apply_rule_changes_relevant_path, 5),
    "COMMIT_IN_ADV": Rule(apply_rule_commit_mentioned_in_adv, 10),
    "COMMIT_IN_REFERENCE": Rule(apply_rule_commit_mentioned_in_reference, 8),
    "VULN_IN_LINKED_ISSUE": Rule(apply_rule_vuln_mentioned_in_linked_issue, 8),
    "SEC_KEYWORD_IN_LINKED_ISSUE": Rule(apply_rule_security_keyword_in_linked_issue, 5),
    "JIRA_ISSUE_IN_COMMIT_MSG_AND_ADV": Rule(
        apply_rule_jira_issue_in_commit_msg_and_adv, 8
    ),
    "SMALL_COMMIT": Rule(apply_rule_small_commit, 1),
}
