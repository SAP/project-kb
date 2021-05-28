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
        changes_relevant_path=True,
        other_CVE_in_message=True,
        commit_falls_in_given_interval_based_on_advisory_publicatation_date=True,
    )

    assert commit_features.commit.repository == "https://github.com/abc/xyz"
    assert commit_features.references_vuln_id
    assert commit_features.time_between_commit_and_advisory_record == 42
    assert commit_features.changes_relevant_path
    assert commit_features.other_CVE_in_message
    assert (
        commit_features.commit_falls_in_given_interval_based_on_advisory_publicatation_date
    )
    assert commit_features.avg_hunk_size == 5
    assert commit_features.n_hunks == 3
    assert commit_features.references_ghissue
    assert commit_features.n_changed_files == 3
    assert commit_features.contains_jira_reference
