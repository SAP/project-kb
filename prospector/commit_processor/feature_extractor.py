from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures


def extract_features(commit: Commit, advisory_record: AdvisoryRecord) -> CommitFeatures:
    reference_to_vuln_id = extract_reference_to_vuln_id(
        commit.cve_refs, advisory_record.vulnerability_id
    )
    commit_feature = CommitFeatures(commit, reference_to_vuln_id)
    return commit_feature


def extract_reference_to_vuln_id(cve_references: "list[str]", cve_id: str) -> str:
    return cve_id in cve_references
