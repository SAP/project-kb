from pprint import pprint

from datamodel.advisory import AdvisoryRecord
from git.git import GIT_CACHE, Git


def prospector(
    vulnerability_id: str,
    repository: str,
    publication_date: str,
    vuln_descr: str,
    use_nvd: bool,
    nvd_rest_endpoint: str,
    git_cache: str = GIT_CACHE,
    verbose: bool = False,
    debug: bool = False,
):
    if verbose:
        debug = True

    advisory_record = AdvisoryRecord(
        vulnerability_id,
        repository,
        published_timestamp=publication_date,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    print("Downloading repository {} in {}..".format(repository, git_cache))
    repository = Git(repository, git_cache)
    repository.clone()
    tags = repository.get_tags()

    if debug:
        print("Found tags:")
        print(tags)

    print("Done")

    # STEP 1: filter based on commit size

    # STEP 2: filter based on time

    # STEP 3: filter based on file extensions

    # TODO take some code from legacy filter.py

    # adv_processor = AdvisoryProcessor()
    # advisory_record = adv_processor.process(advisory_record)

    if debug:
        pprint(advisory_record)


def select_commit_ids_based_on_vulnerability_publish_date(
    vulnerability_published_timestamp,
    git_repo=None,
    repo_url=None,
    days_before=730,
    days_after=100,
    commits_before_cap=5215,
    commits_after_cap=100,
):
    """
    To select commit IDs based on the vulnerability publish date.
    This can be used as a starting position for the search for fix commits.

    Input:
        vulnerability_published_timestamp (int): the timestamp at which the vulnerability is been published i.e. in the NVD
        git_repo (git_explorer.core.Git): to use for extracting the content
        repository_url: if git_repo is not provided, a repository url is needed to initialize the git_repo
        days_before (int): the maximum number of days before the release timestamp (edge)
        days_after (int): the maximum number of days after the release timestamp (edge)
        commits_before_cap (int): the maximum number of commits before the release timestamp (edge)
        commits_after_cap (int): the maximum number of commits after the release timestamp (edge)

    Returns:
        list: a list of commit IDs within the interval
    """

    if git_repo == None:
        try:
            git_repo = Git(repo_url, cache_path=GIT_CACHE)
            git_repo.clone(skip_existing=True)
        except:
            raise TypeError(
                "git-repo should be of type git_explorer.core.Git, not {}, or repo_url should be a valid github repository url.".format(
                    type(git_repo)
                )
            )

    ### Add commits before NVD release
    since, until = database.timestamp_to_timestamp_interval(
        int(vulnerability_published_timestamp), days_before=days_before, days_after=0
    )
    commit_ids_to_add_before = database.get_commit_ids_between_timestamp_interval(
        str(since), str(until), git_repo=git_repo, repository_url=repo_url
    )

    # maximum to add
    if len(commit_ids_to_add_before) > commits_before_cap:
        commit_ids_to_add_before = commit_ids_to_add_before[
            :commits_before_cap
        ]  # add the 5215 closest before the NVD release date

    ### Add commits after NVD release
    since, until = database.timestamp_to_timestamp_interval(
        int(vulnerability_published_timestamp), days_before=0, days_after=days_after
    )
    commit_ids_to_add_after = database.get_commit_ids_between_timestamp_interval(
        str(since), str(until), git_repo=git_repo, repository_url=repo_url
    )

    # maximum to add
    if len(commit_ids_to_add_after) > commits_after_cap:
        commit_ids_to_add_after = commit_ids_to_add_after[
            -commits_after_cap:
        ]  # add the 100 closest before the NVD release date

    commit_ids = commit_ids_to_add_before + commit_ids_to_add_after

    return commit_ids
