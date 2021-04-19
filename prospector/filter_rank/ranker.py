from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from filter_rank.utils.model_loader import save_model
from filter_rank import TRAINING_DATA, NUM_ELEMENTS_TRAINING_DATA

import re
import pandas as pd


def filter_commits(adv_record: AdvisoryRecord, candidates: "list[Commit]") -> "list[Commit]":
    """
    Takes in input a set of candidate (datamodel) commits (coming from the commitdb)
    and returns in output a filtered list obtained by discarding the irrelevant
    ones based on different criteria (timestamp of commit compared to advisory record date,
    extensions of the files modified in the commit, and the like)
    """

    return candidates


def rank(adv_record: AdvisoryRecord, candidates: "list[Commit]") -> "list[Commit]":
    """
    Takes in input a set of candidates and associates to each of them a rank (ordering) and
    a ranking vector, based on how good they match with the advisory record in input.
    """
    return candidates


def train(model_name: str, data_filename=TRAINING_DATA, num_elem_training_data=NUM_ELEMENTS_TRAINING_DATA) -> str:
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


def make_dataframe(data_filename=TRAINING_DATA, num_elem_training_data=NUM_ELEMENTS_TRAINING_DATA):
    """
    This is the helper function to construct the pandas dataframe object for the training data.
    It returns pandas dataframe if succeeds and None otherwise
    """
    commits = []
    try:
        with open(data_filename, 'r', encoding='utf8') as f_in:
            count = 0
            for line in f_in:
                line = line.strip()
                line = re.sub(r"[\['\] ]", "", line).split(",")
                count += 1
                if len(line) < num_elem_training_data:
                    print('[SKIPPING] A problem occurred while reading line {}'.format(count))
                    print(str(line))
                    continue
                cve_id = line[0]
                repo = line[1]
                commit_id = line[2]
                dash = line[3]  # column 3
                technologies = [line[tech] for tech in range(4, len(line) - 1)]  # column 4
                classification = line[-1]

                commits.append([commit_id, repo])
                #   if (commit_id,repo) not found in commitdb:
                #     commit_obj = make_commit(commit_id,repo)
                #     preprocess(commit_obj)
                #     save commit_obj to db
                #   augment commit_obj with advisory-dependent features
    except OSError as e:
        print('An exception occurred while I was trying to extract information from {}'.format(data_filename))
        print(str(e))
        raise OSError('An exception occurred while I was trying to extract information from {}'.format(data_filename))
    if len(commits) > 0:
        return pd.DataFrame(commits, columns=['commit_id', 'repo'])  # This line needs to be updated to correspond to
        # the actual features
    return
