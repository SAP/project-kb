from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def test_simple():
    commit = Commit(
        commit_id="abcd",
        repository="https://github.com/abc/xyz",
        timestamp="124234125",
    )
    commit_features = CommitFeatures(
        commit=commit,
        references_vuln_id=True,
        time_between_commit_and_advisory_record=42,
        changes_relevant_path=True,
        other_CVE_in_message=True,
        commit_falls_in_given_interval_based_on_advisory_publicatation_date=True,
        avg_hunk_size=10,
        n_hunks=12,
        references_ghissue=True,
        n_changed_files=44,
        contains_jira_reference=True,
    )

    assert commit_features.commit.repository == "https://github.com/abc/xyz"
    assert commit_features.references_vuln_id
    assert commit_features.time_between_commit_and_advisory_record == 42
    assert commit_features.changes_relevant_path
    assert commit_features.other_CVE_in_message
    assert (
        commit_features.commit_falls_in_given_interval_based_on_advisory_publicatation_date
    )
    assert commit_features.avg_hunk_size == 10
    assert commit_features.n_hunks == 12
    assert commit_features.references_ghissue
    assert commit_features.n_changed_files == 44
    assert commit_features.contains_jira_reference
