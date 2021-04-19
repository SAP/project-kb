from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def extract_features(commit: Commit, advisory_record: AdvisoryRecord) -> CommitFeatures:
    references_vuln_id = extract_references_vuln_id(
        commit.cve_refs, advisory_record.vulnerability_id
    )
    time_between_commit_and_advisory_record = extract_time_between_commit_and_advisory_record(
        commit.timestamp, advisory_record.published_timestamp
    )
    commit_feature = CommitFeatures(
        commit=commit,
        references_vuln_id=references_vuln_id,
        time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
    )
    return commit_feature


def extract_references_vuln_id(cve_references: "list[str]", cve_id: str) -> str:
    return cve_id in cve_references


def extract_time_between_commit_and_advisory_record(
    commit_timestamp: int, advisory_record_timestamp: int
) -> int:
    return commit_timestamp - advisory_record_timestamp
