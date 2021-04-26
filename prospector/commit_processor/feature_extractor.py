from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def extract_features(commit: Commit, advisory_record: AdvisoryRecord) -> CommitFeatures:
    references_vuln_id = extract_references_vuln_id(
        commit.cve_refs, advisory_record.vulnerability_id
    )
    time_between_commit_and_advisory_record = (
        extract_time_between_commit_and_advisory_record(
            commit.timestamp, advisory_record.published_timestamp
        )
    )
    changes_relevant_path = extract_changes_relevant_path(
        advisory_record.paths, commit.changed_files
    )
    avg_hunk_size = extract_avg_hunk_size(commit.hunks)
    commit_feature = CommitFeatures(
        commit=commit,
        references_vuln_id=references_vuln_id,
        time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
        changes_relevant_path=changes_relevant_path,
        avg_hunk_size=avg_hunk_size,
    )
    return commit_feature


def extract_references_vuln_id(cve_references: "list[str]", cve_id: str) -> bool:
    return cve_id in cve_references


def extract_time_between_commit_and_advisory_record(
    commit_timestamp: int, advisory_record_timestamp: int
) -> int:
    return commit_timestamp - advisory_record_timestamp


def extract_changes_relevant_path(
    relevant_paths: "list[str]", changed_paths: "list[str]"
) -> bool:
    """
    Decides whether any of the changed paths (by a commit) are in the list
    of relevant paths (mentioned in the advisory record)
    """
    return any([changed_path in relevant_paths for changed_path in changed_paths])


def extract_avg_hunk_size(hunks: "list[list[int]]") -> int:
    n_hunks = len(hunks)

    if n_hunks == 0:
        return 0

    lengths = [hunk[1] - hunk[0] for hunk in hunks]
    return sum(lengths) / n_hunks
