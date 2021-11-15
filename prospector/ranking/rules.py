from typing import Dict, List

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from stats.execution import Counter, execution_statistics

from .rule_helpers import (
    extract_commit_mentioned_in_linked_pages,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
    fetch_candidate_references,
)

SEC_KEYWORDS = [
    "vulner",
    "exploit",
    "attack",
    "secur",
    "xxe",
    "dos",
    "insecur",
    "inject",
    "unsafe",
    "remote execution",
    "malicious",
]

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

    print("Enabled rules: " + str(enabled_rules))

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for rule_id in enabled_rules:
                apply_rule_func = enabled_rules[rule_id]
                rule_explanation = apply_rule_func(candidate, advisory_record)
                if rule_explanation:
                    counter.increment("matches")
                    candidate.annotations[rule_id] = rule_explanation

    return candidates


def get_enabled_rules(rules: List) -> Dict:
    enabled_rules = dict()

    if "ALL" in rules:
        enabled_rules = RULES_REGISTRY

    for r in rules:
        print(r)
        print(r[:1])
        if r == "ALL":
            continue
        if r[0] != "-":
            enabled_rules[r] = RULES_REGISTRY[r]
        elif r[0] == "-":
            rule_to_exclude = r[1:]
            if rule_to_exclude in enabled_rules:
                del enabled_rules[rule_to_exclude]

    return enabled_rules


# TODO change signature to accept "Commit", not "CommitWithFeatures"
# in all apply_rule_* funcs
def apply_rule_references_vuln_id(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = (
        "The commit message mentions the vulnerability identifier '{}'"
    )

    references_vuln_id = extract_references_vuln_id(candidate, advisory_record)
    if references_vuln_id:
        return explanation_template.format(advisory_record.vulnerability_id)
    return None


def apply_rule_references_ghissue(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = (
        "The commit message refers to the following GitHub issues: '{}'"
    )

    if len(candidate.ghissue_refs) > 0:
        return explanation_template.format(str(candidate.ghissue_refs))
    return None


def apply_rule_references_jira_issue(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = "The commit message refers to the following Jira issues: {}"

    if len(candidate.jira_refs) > 0:
        return explanation_template.format(", ".join(candidate.jira_refs))
    return None


def apply_rule_changes_relevant_path(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits that touch some file that is mentioned
    in the text of the advisory.
    """

    relevant_paths = []

    explanation_template = "This commit touches the following relevant paths: {}"

    relevant_paths = set(
        [
            path
            for path in candidate.changed_files
            for adv_path in advisory_record.paths
            if adv_path in path
        ]
    )

    if len(relevant_paths) > 0:
        explanation = explanation_template.format(", ".join(relevant_paths))
        return explanation

    return None


def apply_rule_adv_keywords_in_msg(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits whose commit message contain some of the special "code tokens"
    extracted from the advisory.
    """

    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in advisory_record.keywords if kw in candidate.message]
    )

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_adv_keywords_in_diff(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits whose diff contain some of the special "code tokens"
    extracted from the advisory.
    """

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

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_security_keyword_in_msg(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits whose message contains one or more "security-related" keywords
    """

    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in SEC_KEYWORDS if kw in candidate.message.lower()]
    )

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_adv_keywords_in_paths(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits that modify paths that correspond to a code token extracted
    from the advisory.
    """

    explanation_template = "The commit modifies the following paths: {}"

    matches = set(
        [
            (p, token)
            for p in candidate.changed_files
            for token in advisory_record.keywords
            if token in p
        ]
    )

    if len(matches) > 0:
        explained_matches = []

        for m in matches:
            explained_matches.append("{} ({})".format(m[0], m[1]))

        return explanation_template.format(", ".join(explained_matches))

    return None


def apply_rule_commit_mentioned_in_adv(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    explanation_template = (
        "One or more links to this commit appear in the advisory page: ({})"
    )

    commit_references = extract_referred_to_by_nvd(candidate, advisory_record)

    if len(commit_references) > 0:
        return explanation_template.format(", ".join(commit_references))

    return None


def apply_rule_commit_mentioned_in_reference(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    explanation_template = "This commit is mentioned in one or more referenced pages"

    count = extract_commit_mentioned_in_linked_pages(candidate, advisory_record)

    if count > 0:
        return explanation_template

    return None


def apply_rule_vuln_mentioned_in_linked_issue(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    explanation_template = (
        "The issue (or pull request) {} mentions the vulnerability id {}"
    )

    candidate = fetch_candidate_references(candidate)

    for ref, page_content in candidate.ghissue_refs.items():
        if page_content is None:
            continue

        if advisory_record.vulnerability_id in page_content:
            return explanation_template.format(ref, advisory_record.vulnerability_id)

    return None


def apply_rule_security_keyword_in_linked_issue(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    explanation_template = (
        "The issue (or pull request) {} contains security-related terms: {}"
    )

    candidate = fetch_candidate_references(candidate)

    for ref, page_content in candidate.ghissue_refs.items():
        if page_content is None:
            continue

        matching_keywords = set(
            [kw for kw in SEC_KEYWORDS if kw in page_content.lower()]
        )
        if len(matching_keywords) > 0:
            return explanation_template.format(ref, ", ".join(matching_keywords))

    return None


def apply_rule_jira_issue_in_commit_msg_and_advisory(
    candidate: Commit, advisory_record: AdvisoryRecord
) -> str:
    explanation_template = "The issue(s) {} (mentioned in the commit message) is referenced by the advisory"

    matches = [
        (i, j)
        for i in candidate.jira_refs
        for j in advisory_record.references
        if i in j
    ]
    if len(matches) > 0:
        return explanation_template.format(", ".join(matches))

    return None


RULES_REGISTRY = {
    "REF_ADV_VULN_ID": apply_rule_references_vuln_id,
    "TOKENS_IN_DIFF": apply_rule_adv_keywords_in_diff,
    "TOKENS_IN_COMMIT_MSG": apply_rule_adv_keywords_in_msg,
    "TOKENS_IN_MODIFIED_PATHS": apply_rule_adv_keywords_in_paths,
    "SEC_KEYWORD_IN_COMMIT_MSG": apply_rule_security_keyword_in_msg,
    "REF_GH_ISSUE": apply_rule_references_ghissue,
    "REF_JIRA_ISSUE": apply_rule_references_jira_issue,
    "CH_REL_PATH": apply_rule_changes_relevant_path,
    "COMMIT_MENTIONED_IN_ADV": apply_rule_commit_mentioned_in_adv,
    "COMMIT_MENTIONED_IN_REFERENCE": apply_rule_commit_mentioned_in_reference,
    "VULN_MENTIONED_IN_LINKED_ISSUE": apply_rule_vuln_mentioned_in_linked_issue,
    "SEC_KEYWORD_MENTIONED_IN_LINKED_ISSUE": apply_rule_security_keyword_in_linked_issue,
    "JIRA_ISSUE_REF_IN_COMMIT_MSG_AND_ADVISORY": apply_rule_jira_issue_in_commit_msg_and_advisory,
}
