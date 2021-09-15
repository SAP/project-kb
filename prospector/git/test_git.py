# from pprint import pprint

from .git import Git

# from .version_to_tag import version_to_wide_interval_tags
from .version_to_tag import get_tag_for_version


def test_get_commits_in_time_interval():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    results = repo.get_commits(since="1415441712", until="1417441712")

    print("Found %d commits" % len(results))
    assert len(results) == 18


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


def test_extract_timestamp_from_version():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    assert repo.extract_timestamp_from_version("STRUTS_2_3_9") == 1359961896
    assert repo.extract_timestamp_from_version("INVALID_VERSION_1_0_0") is None


def test_get_tag_for_version():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    tags = repo.get_tags()
    assert get_tag_for_version(tags, "2.3.9") == ["STRUTS_2_3_9"]


# def test_legacy_mapping_version_to_tag_1():
#     repo = Git("https://github.com/apache/struts")
#     repo.clone()

#     result = version_to_wide_interval_tags("2.3.34", repo)

#     assert result == [
#         ("STRUTS_2_3_33", "STRUTS_2_3_34"),
#         ("STRUTS_2_3_34", "STRUTS_2_3_35"),
#     ]


# def test_legacy_mapping_version_to_tag_2():
#     repo = Git("https://github.com/apache/struts")
#     repo.clone()

#     result = version_to_wide_interval_tags("2.3.3", repo)

# assert result == [
#     ("STRUTS_2_3_2", "STRUTS_2_3_3"),
#     ("STRUTS_2_3_3", "STRUTS_2_3_4"),
# ]


def test_get_commit_parent():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    # https://github.com/apache/struts/commit/bef7211c41e7b0df9ff2740c0d4843f5b7a43266
    commit = repo.get_commit(repo.get_commit_id_for_tag("STRUTS_2_3_9"))

    parent_id = commit.get_parent_id()
    assert len(parent_id) == 1
    assert parent_id[0] == "77d51c4222e3356b3842f0784bf37a9af212d867"
    # print(parent_id)

    print(repo.get_commit("2ba1a3eaf5cb53aa8701e652293988b781c54f37"))

    commits = repo.get_commits_between_two_commit(
        "2ba1a3eaf5cb53aa8701e652293988b781c54f37",
        "04bc4bd97c41bd181dd45580ce12236218177aca",
    )

    print(commits[2])

    # Works well on merge commit too
    # https://github.com/apache/struts/commit/cb318cdc749f40a06eaaeed789a047f385a55480
    commit = repo.get_commit("cb318cdc749f40a06eaaeed789a047f385a55480")
    parent_id = commit.get_parent_id()
    assert len(parent_id) == 2
    assert parent_id[0] == "05528157f0725707a512aa4dc2b9054fb4a4467c"
    assert parent_id[1] == "fe656eae21a7a287b2143fad638234314f858178"
    # print(parent_id)
