import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import Git

from .feature_extractor import (
    extract_changed_relevant_paths,
    extract_features,
    extract_other_CVE_in_message,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
    extract_referred_to_by_pages_linked_from_advisories,
    extract_time_between_commit_and_advisory_record,
    is_commit_in_given_interval,
    is_commit_reachable_from_given_tag,
)
from .preprocessor import preprocess_commit


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


def test_extract_features(repository, requests_mock):
    requests_mock.get(
        "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62"
    )
    requests_mock.get(
        "https://for.testing.purposes/containing_commit_id_in_text",
        text="some text 7532d2fb0d6081a12c2a48ec854a81a8b718be62 blah",
    )

    repo = repository
    commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
    processed_commit = preprocess_commit(commit)

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references=[
            "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62",
            "https://for.testing.purposes/containing_commit_id_in_text",
        ],
        paths=["pom.xml"],
    )

    extracted_features = extract_features(processed_commit, advisory_record)

    assert extracted_features.references_vuln_id is True
    assert extracted_features.time_between_commit_and_advisory_record == 1000000
    assert extracted_features.changes_relevant_path == [
        "pom.xml",
    ]
    assert extracted_features.other_CVE_in_message == [
        "CVE-2020-26259",
    ]
    assert extracted_features.referred_to_by_pages_linked_from_advisories == [
        "https://for.testing.purposes/containing_commit_id_in_text",
    ]
    assert extracted_features.referred_to_by_nvd == [
        "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62",
    ]


def test_extract_references_vuln_id():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=[
            "test_advisory_record",
            "another_advisory_record",
            "yet_another_advisory_record",
        ],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="test_advisory_record")
    result = extract_references_vuln_id(commit, advisory_record)
    assert result is True


def test_time_between_commit_and_advisory_record():
    commit = Commit(
        commit_id="test_commit", repository="test_repository", timestamp=142
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", published_timestamp=100
    )
    assert (
        extract_time_between_commit_and_advisory_record(commit, advisory_record) == 42
    )


@pytest.fixture
def paths():
    return [
        "fire-nation/zuko/lightning.png",
        "water-bending/katara/necklace.gif",
        "air-nomad/aang/littlefoot.jpg",
        "earth-kingdom/toph/metal.png",
    ]


@pytest.fixture
def sub_paths():
    return [
        "lightning.png",
        "zuko/lightning.png",
        "fire-nation/zuko",
        "water-bending",
    ]


class TestExtractChangedRelevantPaths:
    @staticmethod
    def test_sub_path_matching(paths, sub_paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=paths
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=sub_paths
        )

        matched_paths = {
            "fire-nation/zuko/lightning.png",
            "water-bending/katara/necklace.gif",
        }

        assert extract_changed_relevant_paths(commit, advisory_record) == matched_paths

    @staticmethod
    def test_same_path_only(paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=paths
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[:2]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set(paths[:2])

    @staticmethod
    def test_same_path_and_others(paths):
        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=[paths[0]],
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[:2]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == {
            paths[0],
        }

    @staticmethod
    def test_no_match(paths):
        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=paths[:1],
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[2:]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()

    @staticmethod
    def test_empty_list(paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=[]
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()

        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=paths,
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=[]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()


def test_extract_other_CVE_in_message():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=["CVE-2021-29425", "CVE-2021-21251"],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2020-31284")
    assert extract_other_CVE_in_message(commit, advisory_record) == {
        "CVE-2021-29425",
        "CVE-2021-21251",
    }
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2021-29425")
    result = extract_other_CVE_in_message(commit, advisory_record)
    assert result == {
        "CVE-2021-21251",
    }


def test_is_commit_in_given_interval():
    assert is_commit_in_given_interval(1359961896, 1359961896, 0)
    assert is_commit_in_given_interval(1359961896, 1360047896, 1)
    assert is_commit_in_given_interval(1359961896, 1359875896, -1)
    assert not is_commit_in_given_interval(1359961896, 1359871896, -1)
    assert not is_commit_in_given_interval(1359961896, 1360051896, 1)


def test_extract_referred_to_by_nvd(repository):
    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        references=[
            "https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E",
            "https://other.com",
        ],
    )

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert extract_referred_to_by_nvd(commit, advisory_record) == {
        "https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E",
    }

    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert extract_referred_to_by_nvd(commit, advisory_record) == set()


def test_is_commit_reachable_from_given_tag(repository):

    repo = repository
    commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
    test_commit = preprocess_commit(commit)

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        paths=["pom.xml"],
        published_timestamp=1000000,
        versions=["STRUTS_2_1_3", "STRUTS_2_3_9"],
    )

    assert not is_commit_reachable_from_given_tag(
        test_commit, advisory_record, advisory_record.versions[0]
    )

    assert is_commit_reachable_from_given_tag(
        preprocess_commit(repo.get_commit("2e19fc6670a70c13c08a3ed0927abc7366308bb1")),
        advisory_record,
        advisory_record.versions[1],
    )


def test_extract_referred_to_by_pages_linked_from_advisories(repository, requests_mock):
    requests_mock.get(
        "https://for.testing.purposes/containing_commit_id_in_text_2",
        text="some text r97993e3d78e1f5389b7b172ba9f308440830ce5 blah",
    )

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        references=["https://for.testing.purposes/containing_commit_id_in_text_2"],
    )

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert extract_referred_to_by_pages_linked_from_advisories(
        commit, advisory_record
    ) == {
        "https://for.testing.purposes/containing_commit_id_in_text_2",
    }

    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert (
        extract_referred_to_by_pages_linked_from_advisories(commit, advisory_record)
        == set()
    )


def test_extract_referred_to_by_pages_linked_from_advisories_wrong_url(repository):
    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        references=["https://non-existing-url.com"],
    )

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert not extract_referred_to_by_pages_linked_from_advisories(
        commit, advisory_record
    )
