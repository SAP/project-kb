from .git import Git, version_to_wide_interval_tags
from pprint import pprint


def test_get_commits_in_time_interval():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    results = repo.get_commits(since="1615441712", until="1617441712",)

    print("Found %d commits" % len(results))
    assert len(results) == 20


def test_get_commits_in_time_interval_filter_extension():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    results = repo.get_commits(
        since="1615441712", until="1617441712", filter_files="*.xml"
    )

    print("Found %d commits" % len(results))
    for c in results:
        print("{}/commit/{}".format(repo.get_url(), c))
    assert len(results) == 5


def test_legacy_mapping_version_to_tag_1():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    result = version_to_wide_interval_tags("2.3.34", repo)

    assert result == [
        ("STRUTS_2_3_33", "STRUTS_2_3_34"),
        ("STRUTS_2_3_34", "STRUTS_2_3_35"),
    ]


def test_legacy_mapping_version_to_tag_2():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    result = version_to_wide_interval_tags("2.3.3", repo)

    assert result == [
        ("STRUTS_2_3_2", "STRUTS_2_3_3"),
        ("STRUTS_2_3_3", "STRUTS_2_3_4"),
    ]
