from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from stats.execution import Counter, execution_statistics

from .rule_helpers import (
    extract_commit_mentioned_in_linked_pages,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
)

"""
QUICK GUIDE: HOW TO IMPLEMENT A NEW RULE

1. Start by adding an entry to the RULES dictionary in the apply_rule function.
   Pick a clear rule id (all capitals, underscore separated) and a rule function
   (start with apply_rule_....)

2. Implement the rule function, which MUST take as input a datamodel.commit.Commit
   and an AdvisoryRecord and must return either None, if the rule did not match,
   or a string explaining the match that was found.

3. Do not forget to write a short comment at the beginning of the function explaining
   what the rule is about.

IMPORTANT: you are not supposed to change the content of function apply_rules, except
adding entries to its inner RULES dictionary.
"""

rule_statistics = execution_statistics.sub_collection("rules")


def apply_rules(
    candidates: "list[Commit]",
    advisory_record: AdvisoryRecord,
    active_rules=["ALL"],
) -> "list[Commit]":
    """
    This applies a set of hand-crafted rules and returns a dict in the following form:

    commits_ruled[candidate] = ["explanation"]

    where 'explanation' describes the rule that matched for that candidate
    """

    RULES = {
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
    }

    if "ALL" in active_rules:
        rules = RULES
    else:
        rules = dict()
        for i in RULES:
            if i in active_rules:
                rules[i] = RULES[i]
    rule_statistics.collect("active", len(rules), unit="rules")

    # print("Enabled rules: " + str(rules))

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for rule_id in rules:
                apply_rule_func = rules[rule_id]
                rule_explanation = apply_rule_func(candidate, advisory_record)
                if rule_explanation:
                    counter.increment("matches")
                    candidate.annotations[rule_id] = rule_explanation

    return candidates


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

    explanation_template = "The commit diff includes the following keywords: {}"

    matching_keywords = set(
        [
            kw
            for kw in advisory_record.keywords
            for diff_line in candidate.diff
            if kw in diff_line
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

    SEC_KEYWORDS = [
        "vuln",
        "exploit",
        "attack",
        "secur",
        "xxe",
        "dos",
        "insecur",
        "inject",
    ]
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
