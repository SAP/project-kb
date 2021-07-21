from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures

"""
QUICK GUIDE: HOW TO IMPLEMENT A NEW RULE

1. Start by adding an entry to the RULES dictionary in the apply_rule function.
   Pick a clear rule id (all capitals, underscore separated) and a rule function
   (start with apply_rule_....)

2. Implement the rule function, which MUST take as input a CommitWithFeatures
   and an AdvisoryRecord and must return either None, if the rule did not match,
   or a string explaining the match that was found.

3. Do not forget to write a short comment at the beginning of the function explaining
   what the rule is about.

IMPORTANT: you are not supposed to change the content of function apply_rules, except
adding entries to its inner RULES dictionary.
"""


def apply_rules(
    candidates: "list[CommitWithFeatures]",
    advisory_record: AdvisoryRecord,
    active_rules=["ALL"],
) -> "list[CommitWithFeatures]":
    """
    This applies a set of hand-crafted rules and returns a dict in the following form:

    commits_ruled[candidate] = ["explanation"]

    where 'explanation' describes the rule that matched for that candidate
    """

    RULES = {
        "REF_ADV_VULN_ID": apply_rule_references_vuln_id,
        "TOKENS_IN_DIFF": apply_rule_code_tokens_in_diff,
        "TOKENS_IN_COMMIT_MSG": apply_rule_code_tokens_in_msg,
        "SEC_KEYWORD_IN_COMMIT_MSG": apply_rule_security_keyword_in_msg,
        "REF_GH_ISSUE": apply_rule_references_ghissue,
        "REF_JIRA_ISSUE": apply_rule_references_jira_issue,
        "CH_REL_PATH": apply_rule_changes_relevant_path,
    }

    if "ALL" in active_rules:
        rules = RULES
    else:
        rules = dict()
        for i in RULES:
            if i in active_rules:
                rules[i] = RULES[i]

    # print("Enabled rules: " + str(rules))

    for candidate in candidates:
        for rule_id in rules:
            apply_rule_func = rules[rule_id]
            rule_explanation = apply_rule_func(candidate, advisory_record)
            if rule_explanation:
                candidate.annotations[rule_id] = rule_explanation

    return candidates


def apply_rule_references_vuln_id(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = (
        "The commit message mentions the vulnerability identifier '{}'"
    )

    if candidate.references_vuln_id:
        return explanation_template.format(advisory_record.vulnerability_id)
    return None


def apply_rule_references_ghissue(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = (
        "The commit message refers to the following GitHub issues: '{}'"
    )

    if len(candidate.commit.ghissue_refs) > 0:
        return explanation_template.format(str(candidate.commit.ghissue_refs))
    return None


def apply_rule_references_jira_issue(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
) -> str:

    explanation_template = "The commit message refers to the following Jira issues: {}"

    if len(candidate.commit.jira_refs) > 0:
        return explanation_template.format(", ".join(candidate.commit.jira_refs))
    return None


def apply_rule_changes_relevant_path(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
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
            for path in candidate.commit.changed_files
            for adv_path in advisory_record.paths
            if adv_path in path
        ]
    )

    if len(relevant_paths) > 0:
        explanation = explanation_template.format(", ".join(relevant_paths))
        return explanation

    return None


def apply_rule_code_tokens_in_msg(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits whose commit message contain some of the special "code tokens"
    extracted from the advisory.
    """

    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in advisory_record.code_tokens if kw in candidate.commit.message]
    )

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_code_tokens_in_diff(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
) -> str:
    """
    This rule matches commits whose diff contain some of the special "code tokens"
    extracted from the advisory.
    """

    explanation_template = "The commit diff includes the following keywords: {}"

    matching_keywords = set(
        [
            kw
            for kw in advisory_record.code_tokens
            for diff_line in candidate.commit.diff
            if kw in diff_line
        ]
    )

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None


def apply_rule_security_keyword_in_msg(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
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
        [kw for kw in SEC_KEYWORDS if kw in candidate.commit.message.lower()]
    )

    if len(matching_keywords) > 0:
        return explanation_template.format(", ".join(matching_keywords))

    return None
