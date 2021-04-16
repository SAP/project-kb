import base64
import json
import pickle
import sys
from datetime import datetime
from pprint import pprint

import requests
from fastapi.encoders import jsonable_encoder

from commit_processor.preprocessor import preprocess_commit
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import GIT_CACHE
from git.git import Commit as GitCommit
from git.git import Git

SECS_PER_DAY = 86400

# TODO make this controllable from the client
TIME_LIMIT_BEFORE = 365 * SECS_PER_DAY
TIME_LIMIT_AFTER = 90 * SECS_PER_DAY

MAX_CANDIDATES = 1000


def prospector(
    vulnerability_id: str,
    repository_url: str,
    publication_date: str = "",
    vuln_descr: str = "",
    use_nvd: bool = False,
    nvd_rest_endpoint: str = "",
    git_cache: str = GIT_CACHE,
    verbose: bool = False,
    debug: bool = True,
) -> "list[Commit]":

    if debug:
        verbose = True

    advisory_record = AdvisoryRecord(
        vulnerability_id,
        repository_url,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    if debug:
        pprint(advisory_record)

    if publication_date != "":
        advisory_record.published_timestamp = int(
            datetime.strptime(publication_date, r"%Y-%m-%dT%H:%M%z").timestamp()
        )

    advisory_record.analyze(use_nvd=True)

    print("Downloading repository {} in {}..".format(repository_url, git_cache))
    repository = Git(repository_url, git_cache)
    repository.clone()
    tags = repository.get_tags()

    if debug:
        print("Found tags:")
        print(tags)

    print("Done retrieving %s" % repository_url)

    # STEP 1: filter based on time and on file extensions
    if advisory_record.published_timestamp:
        since = advisory_record.published_timestamp - TIME_LIMIT_BEFORE
        until = advisory_record.published_timestamp + TIME_LIMIT_AFTER
        candidates = repository.get_commits(since=since, until=until, filter_files="")
    else:
        candidates = repository.get_commits()

    if debug:
        print("Collected %d candidates" % len(candidates))

    if len(candidates) > MAX_CANDIDATES:
        print("Number of candidates exceeds %d, aborting." % MAX_CANDIDATES)
        sys.exit(-1)

    preprocessed_commits: "list[GitCommit]" = []
    for commit_id in candidates:
        if verbose:
            print("Preprocessing " + commit_id, flush=True)
        preprocessed_commits.append(preprocess_commit(repository.get_commit(commit_id)))

    # adv_processor = AdvisoryProcessor()
    # advisory_record = adv_processor.process(advisory_record)

    if debug:
        # TODO clean this up
        pprint(advisory_record)
        # print("Printing the first 10 candidates")
        # pprint(candidates[:10])
        # pprint(preprocessed_commits[0])

    if verbose:
        print("preprocessed %d commits" % len(preprocessed_commits))

    payload = [c.__dict__ for c in preprocessed_commits]

    # TODO read backend address from config file
    r = requests.post("http://localhost:8000/commits/", json=payload)
    print("Status: %d" % r.status_code)

    # TODO compute actual rank
    ranked_results = candidates

    return ranked_results
