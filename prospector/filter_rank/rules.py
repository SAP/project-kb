from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures


def apply_rules(
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

        if "ALL" in rules or "CH_REL_PATH" in rules:
            tag, rule_explanation = apply_rule_changes_relevant_path(
                candidate, advisory_record
            )
            if tag:
                candidate.annotations[tag] = rule_explanation

        # annotated_candidates.append(candidate)
    # NOTE: the CommitWithFeatures object has a handy member variable "commit"
    # which gives access to the underlying "raw" commit object
    return candidates


def apply_rule_references_vuln_id(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    rule_tag = "REF_ADV_VULN_ID"
    if candidate.references_vuln_id:
        explanation_template = "This commit message contains the string '{}' that is the \
        vulnerability identifier mentioned in the advisory"
        explanation = explanation_template.format(advisory_record.vulnerability_id)
        return rule_tag, explanation
    return None, None


def apply_rule_references_ghissue(candidate: CommitWithFeatures):
    rule_tag = "REF_GH_ISSUE"
    if candidate.references_ghissue:
        explanation_template = (
            "This commit has references to the following GitHub issues: '{}'"
        )
        explanation = explanation_template.format(str(candidate.commit.ghissue_refs))
        return rule_tag, explanation
    return None, None


def apply_rule_changes_relevant_path(
    candidate: CommitWithFeatures, advisory_record: AdvisoryRecord
):
    rule_tag = "CH_REL_PATH"
    if candidate.changes_relevant_path:
        explanation_template = "This commit touches the following relevant paths: '{}'"
        relevant_paths = [
            changed_path in advisory_record.paths
            for changed_path in candidate.commit.changed_files
        ]
        explanation = explanation_template.format(str(relevant_paths))
        return rule_tag, explanation
    return None, None
