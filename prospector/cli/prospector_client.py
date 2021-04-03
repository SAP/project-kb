from datamodel.advisory import AdvisoryRecord
from git.git import Git, GIT_CACHE
from pprint import pprint


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
    print(tags)
    print("Done")

    # TODO take some code from legacy filter.py

    # adv_processor = AdvisoryProcessor()
    # advisory_record = adv_processor.process(advisory_record)

    if debug:
        pprint(advisory_record)
