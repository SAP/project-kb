from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit


def filter(adv_record: AdvisoryRecord, candidates: "list[Commit]") -> "list[Commit]":
    """
    Takes in input a set of candidate (datamodel)commits (coming from the commitdb)
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


def train(model_name: str, data_filename: str) -> bool:
    """
    Takes in input a dataset and produces a trained model that is persisted to disk.
    Dataset file contains triples:  (vuln_id,repository,commit_id)
    """
    # read data_filename content in list of lines
    # foreach l in line:
    #   get (commit_id,repo) from l
    #   if (commit_id,repo) not found in commidb:
    #     commit_obj = make_commit(commit_id,repo)
    #     preprocess(commit_obj)
    #     save commit_obj to db
    #   augment commit_obj with advisory-dependent features
    #   add augmented commit_obj to dataframe
    # fit(dataframe) --> model
    # compute metrics
    # save model to disk (file: model_name.bin)
    return True
