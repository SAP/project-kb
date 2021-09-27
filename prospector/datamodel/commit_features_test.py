from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures


def test_simple():
    commit = Commit(
        commit_id="abcd",
        repository="https://github.com/abc/xyz",
        timestamp="124234125",
        hunk_count=3,
        hunks=[(1, 5), (3, 8), (3, 9)],
        changed_files=["pom.xml", "one.java", "two.php"],
        ghissue_refs=["#365", "#42"],
        jira_refs=["ABC-123", "CBA-456"],
    )
    commit_features = CommitWithFeatures(
        commit=commit,
        references_vuln_id=True,
        time_between_commit_and_advisory_record=42,
        changes_relevant_path={"foo/bar/otherthing.xml", "pom.xml"},
        other_CVE_in_message={"CVE-2021-42", "CVE-2021-20210514"},
        referred_to_by_pages_linked_from_advisories={"http://foo.com", "http://bar.hu"},
        referred_to_by_nvd=[
            "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62"
        ],
    )

    # TODO: recheck these assert
    assert commit_features.commit.repository == "https://github.com/abc/xyz"
    assert commit_features.references_vuln_id is True
    assert commit_features.time_between_commit_and_advisory_record == 42
    assert set(commit_features.changes_relevant_path) == {
        "foo/bar/otherthing.xml",
        "pom.xml",
    }
    assert set(commit_features.other_CVE_in_message) == {
        "CVE-2021-42",
        "CVE-2021-20210514",
    }
    assert (
        "http://foo.com" in commit_features.referred_to_by_pages_linked_from_advisories
    )
    assert (
        "http://bar.hu" in commit_features.referred_to_by_pages_linked_from_advisories
    )

    assert commit_features.referred_to_by_nvd == [
        "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62"
    ]
