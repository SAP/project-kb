from datetime import datetime
from pprint import pprint

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import GIT_CACHE, Git

SECS_PER_DAY = 86400

# TODO make this controllable from the client
TIME_LIMIT_BEFORE = 2 * 365 * SECS_PER_DAY
TIME_LIMIT_AFTER = 120 * SECS_PER_DAY


def prospector(
    vulnerability_id: str,
    repository: str,
    publication_date: str = "",
    vuln_descr: str = "",
    use_nvd: bool = False,
    nvd_rest_endpoint: str = "",
    git_cache: str = GIT_CACHE,
    verbose: bool = False,
    debug: bool = False,
) -> "list[Commit]":

    if verbose:
        debug = True

    advisory_record = AdvisoryRecord(
        vulnerability_id,
        repository,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    if publication_date != "":
        advisory_record.published_timestamp = int(
            datetime.strptime(publication_date, r"%Y-%m-%dT%H:%M%z").timestamp()
        )

    advisory_record.analyze(use_nvd=True)

    print("Downloading repository {} in {}..".format(repository, git_cache))
    repository = Git(repository, git_cache)
    repository.clone()
    tags = repository.get_tags()

    if debug:
        print("Found tags:")
        print(tags)

    print("Done retrieving %s", repository)

    # STEP 1: filter based on time and on file extensions
    since = advisory_record.published_timestamp - TIME_LIMIT_BEFORE
    until = advisory_record.published_timestamp - TIME_LIMIT_AFTER
    candidates = repository.get_commits(since=since, until=until, filter_files="")

    # STEP 2: filter based on commit size

    # TODO take some code from legacy filter.py

    # adv_processor = AdvisoryProcessor()
    # advisory_record = adv_processor.process(advisory_record)

    if debug:
        pprint(advisory_record)
        pprint(candidates[:10])

    return []
