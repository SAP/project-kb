import random
import re

import pandas as pd

from datamodel.commit_features import CommitWithFeatures
from filter_rank import NUM_ELEMENTS_TRAINING_DATA, TRAINING_DATA

from .utils.model_loader import save_model


def rank(
    candidates: "list[CommitWithFeatures]", model_name: str
) -> "list[CommitWithFeatures]":
    """
    Takes in input a set of candidates and associates to each of them a rank (ordering) and
    a ranking vector, based on how good they match with the advisory record in input.
    Returns the initial list of commits in the order of their ranks
    """
    scores = []
    for candidate in candidates:
        scores.append((predict(model_name, candidate), candidate))

    return [c for _, c in sorted(scores, reverse=True)]


def predict(model_name: str, commit_features: CommitWithFeatures) -> float:
    """
    The function computes the similarity score for the given commit
    """
    # model = load_model(model_name)

    # compute the actual value here
    # value = model.predict(commit_features)

    return (
        random.random() * 2 - 1
    )  # currently, I am simply returning a random value in the range [-1; 1]


def train(
    model_name: str,
    data_filename=TRAINING_DATA,
    num_elem_training_data=NUM_ELEMENTS_TRAINING_DATA,
) -> str:
    """
    Takes in input a dataset and produces a trained model that is persisted to disk.
    Dataset file contains triples:  (vuln_id,fix_id,repository,commit_id)
    Returns the path to the saved model
    """
    # read data_filename content in list of lines
    # foreach l in line:
    #   get (commit_id,repo) from l
    #   if (commit_id,repo) not found in commitdb:
    #     commit_obj = make_commit(commit_id,repo)
    #     preprocess(commit_obj)
    #     save commit_obj to db
    #   augment commit_obj with advisory-dependent features
    #   add augmented commit_obj to dataframe
    # fit(dataframe) --> model
    # compute metrics
    # save model to disk (file: model_name)
    df = make_dataframe(data_filename, num_elem_training_data)
    if df is None:
        return ""  # Special case, when returned dataframe is None

    model = ""  # here should go the actual classifier model
    # model.fit(df)
    # compute metrics
    return save_model(model, model_name)


def make_dataframe(
    data_filename=TRAINING_DATA, num_elem_training_data=NUM_ELEMENTS_TRAINING_DATA
):
    """
    This is the helper function to construct the pandas dataframe object for the training data.
    It returns pandas dataframe if succeeds and None otherwise
    """
    commits = []
    try:
        with open(data_filename, "r", encoding="utf8") as f_in:
            count = 0
            for line in f_in:
                line = line.strip()
                line = re.sub(r"[\['\] ]", "", line).split(",")
                count += 1
                if len(line) < num_elem_training_data:
                    print(
                        "[SKIPPING] A problem occurred while reading line {}".format(
                            count
                        )
                    )
                    print(str(line))
                    continue
                # cve_id = line[0]
                repo = line[1]
                commit_id = line[2]
                # dash = line[3]  # column 3
                # technologies = [line[tech] for tech in range(4, len(line) - 1)]  # column 4
                # classification = line[-1]

                commits.append([commit_id, repo])
                #   if (commit_id,repo) not found in commitdb:
                #     commit_obj = make_commit(commit_id,repo)
                #     preprocess(commit_obj)
                #     save commit_obj to db
                #   augment commit_obj with advisory-dependent features
    except OSError as e:
        print(
            "An exception occurred while I was trying to extract information from {}".format(
                data_filename
            )
        )
        print(str(e))
        raise OSError(
            "An exception occurred while I was trying to extract information from {}".format(
                data_filename
            )
        )
    if len(commits) > 0:
        return pd.DataFrame(
            commits, columns=["commit_id", "repo"]
        )  # This line needs to be updated to correspond to
        # the actual features
    return


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

        if "ALL" in rules or "REF_VULN_ID" in rules:
            rule_explanation = apply_rule_references_vuln_id(candidate)
            if rule_explanation:
                candidate.annotations.append(rule_explanation)

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
