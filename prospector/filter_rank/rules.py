from datamodel.commit_features import CommitWithFeatures


def apply_rules(
    candidates: "list[CommitWithFeatures]", rules=["ALL"]
) -> "list[CommitWithFeatures]":
    """
    This applies a set of hand-crafted rules and returns a dict in the following form:

    rule_application_result[candidate] = ["explanation"]

    where 'explanation' describes the rule that matched for that candidate
    """

    # TODO modify so that the list in output is identical to the one in input,
    # except that some (or all) of the items might have additional annotations
    # that they did not have in the input list
    # The user will be in charge of deciding how to use those annotations
    # when displaying/sorting the results.

    results = dict()
    for candidate in candidates:
        # Below goes the code to extract commits that correspond to a particular rule
        # To add a new rule, one needs to add the following code snippet:
        # if rules == "ALL" or "Rule name" in rules:
        #    apply_rule(candidate, rule_application_result)

        if "ALL" in rules or "REF_VULN_ID" in rules:
            rule_explanation = apply_rule_references_vuln_id(candidate)
            if rule_explanation:
                if candidate not in results:
                    results[candidate] = []
                results[candidate].append(rule_explanation)

        if "ALL" in rules or "REF_GH_ISSUE" in rules:
            rule_explanation = apply_rule_references_ghissue(candidate)
            if rule_explanation:
                if candidate not in results:
                    results[candidate] = []
                results[candidate].append(rule_explanation)

        if "ALL" in rules or "CH_REL_PATH" in rules:
            rule_explanation = apply_rule_changes_relevant_path(candidate)
            if rule_explanation:
                if candidate not in results:
                    results[candidate] = []
                results[candidate].append(rule_explanation)
    # NOTE: the CommitWithFeatures object has a handy member variable "commit"
    # which gives access to the underlying "raw" commit object
    return results


def apply_rule_references_vuln_id(candidate: CommitWithFeatures):
    if candidate.references_vuln_id:
        return "Vuln ID is mentioned"
    return None


def apply_rule_references_ghissue(candidate: CommitWithFeatures):
    if candidate.references_ghissue:
        return "GitHub issue is mentioned"
    return None


def apply_rule_changes_relevant_path(candidate: CommitWithFeatures):
    if candidate.changes_relevant_path:
        return "Relevant path has been changed"
    return None
