from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures


def apply_rules(  # noqa: C901
    candidates: "list[CommitWithFeatures]",
    advisory_record: AdvisoryRecord,
    rules=["ALL"],
) -> "list[CommitWithFeatures]":
    """
    This applies a set of hand-crafted rules and returns a dict in the following form:

    commits_ruled[candidate] = ["explanation"]

    where 'explanation' describes the rule that matched for that candidate
    """
    # annotated_candidates = []
    for candidate in candidates:
        # Below goes the code to extract commits that correspond to a particular rule
        # To add a new rule, one needs to add the following code snippet:
        # if rules == "ALL" or "Rule name" in rules:
        #    apply_rule(candidate, rule_application_result)

        if "ALL" in rules or "REF_ADV_VULN_ID" in rules:
            tag, rule_explanation = apply_rule_references_vuln_id(
                candidate, advisory_record
            )
            if tag:
                candidate.annotations[tag] = rule_explanation

        if "ALL" in rules or "REF_GH_ISSUE" in rules:
            tag, rule_explanation = apply_rule_references_ghissue(candidate)
            if tag:
                candidate.annotations[tag] = rule_explanation

        if "ALL" in rules or "REF_JIRA_ISSUE" in rules:
            tag, rule_explanation = apply_rule_references_jira_issue(candidate)
            if tag:
                candidate.annotations[tag] = rule_explanation

        if "ALL" in rules or "CH_REL_PATH" in rules:
            tag, rule_explanation = apply_rule_changes_relevant_path(
                candidate, advisory_record
            )
            if tag:
                candidate.annotations[tag] = rule_explanation

        if "ALL" in rules or "TOKENS_IN_COMMIT_MSG" in rules:
            tag, rule_explanation = apply_rule_code_tokens_in_msg(
                candidate, advisory_record
            )
            if tag:
                candidate.annotations[tag] = rule_explanation

        if "ALL" in rules or "TOKENS_IN_DIFF" in rules:
            tag, rule_explanation = apply_rule_code_tokens_in_diff(
                candidate, advisory_record
            )
            if tag:
                candidate.annotations[tag] = rule_explanation

    # NOTE: the CommitWithFeatures object has a handy member variable "commit"
    # which gives access to the underlying "raw" commit object
    return candidates


def apply_rule_references_vuln_id(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    rule_tag = "REF_ADV_VULN_ID"
    if candidate.references_vuln_id:
        explanation_template = (
            "The commit message mentions the vulnerability identifier '{}'"
        )
        explanation = explanation_template.format(advisory_record.vulnerability_id)
        return rule_tag, explanation
    return None, None


def apply_rule_references_ghissue(candidate: CommitWithFeatures):
    rule_tag = "REF_GH_ISSUE"
    if len(candidate.commit.ghissue_refs) > 0:
        explanation_template = (
            "The commit message refers to the following GitHub issues: '{}'"
        )
        explanation = explanation_template.format(str(candidate.commit.ghissue_refs))
        return rule_tag, explanation
    return None, None


def apply_rule_references_jira_issue(candidate: CommitWithFeatures):
    rule_tag = "REF_JIRA_ISSUE"
    if len(candidate.commit.jira_refs) > 0:
        explanation_template = (
            "The commit message refers to the following Jira issues: {}"
        )
        explanation = explanation_template.format(", ".join(candidate.commit.jira_refs))
        return rule_tag, explanation
    return None, None


def apply_rule_changes_relevant_path(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    """
    This rule matches commits that touch some file that is mentioned
    in the text of the advisory.
    """

    rule_tag = "CH_REL_PATH"
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
        return rule_tag, explanation

    return None, None


def apply_rule_code_tokens_in_msg(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    """
    This rule matches commits whose commit message contain some of the special "code tokens"
    extracted from the advisory.
    """

    rule_tag = "KEYWORDS_IN_COMMIT_MSG"
    explanation_template = "The commit message includes the following keywords: {}"

    matching_keywords = set(
        [kw for kw in advisory_record.code_tokens if kw in candidate.commit.message]
    )

    if len(matching_keywords) > 0:
        explanation = explanation_template.format(", ".join(matching_keywords))
        return rule_tag, explanation

    return None, None


def apply_rule_code_tokens_in_diff(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    """
    This rule matches commits whose diff contain some of the special "code tokens"
    extracted from the advisory.
    """

    rule_tag = "KEYWORDS_IN_DIFF"
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
        explanation = explanation_template.format(", ".join(matching_keywords))
        return rule_tag, explanation

    return None, None
