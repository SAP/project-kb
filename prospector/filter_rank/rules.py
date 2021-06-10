from datamodel.commit_features import CommitWithFeatures


def apply_rules(
    candidates: "list[CommitWithFeatures]", rules=["ALL"]
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
            tag, rule_explanation = apply_rule_references_vuln_id(candidate)
            if rule_explanation:
                candidate.annotations.append((tag, rule_explanation))

        if "ALL" in rules or "REF_GH_ISSUE" in rules:
            rule_explanation = apply_rule_references_ghissue(candidate)
            if rule_explanation:
                candidate.annotations.append(rule_explanation)

        if "ALL" in rules or "CH_REL_PATH" in rules:
            rule_explanation = apply_rule_changes_relevant_path(candidate)
            if rule_explanation:
                candidate.annotations.append(rule_explanation)

        # annotated_candidates.append(candidate)
    # NOTE: the CommitWithFeatures object has a handy member variable "commit"
    # which gives access to the underlying "raw" commit object
    return candidates


def apply_rule_references_vuln_id(candidate: CommitWithFeatures):
    rule_tag = "REF_ADV_VULN_ID"
    if len(candidate.references_vuln_id) > 0:
        explanation_template = "This commit message contains the string '{}' that is the \
        vulnerability identifier mentioned in the advisory"
        explanation = explanation_template.format(candidate.references_vuln_id)
        return rule_tag, explanation
    return None, None


def apply_rule_references_ghissue(candidate: CommitWithFeatures):
    rule_tag = "REF_GH_ISSUE"
    if candidate.references_ghissue:
        return rule_tag, "GitHub issue is mentioned"
    return None, None


def apply_rule_changes_relevant_path(candidate: CommitWithFeatures):
    rule_tag = "CH_REL_PATH"
    if candidate.changes_relevant_path:
        return rule_tag, "Relevant path has been changed"
    return None, None
