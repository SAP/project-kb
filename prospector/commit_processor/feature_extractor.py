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
    commit_falls_in_given_interval_based_on_advisory_publicatation_date = (
        extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
            commit.timestamp, advisory_record, 180, 365
        )
    )
    changes_relevant_path = extract_changes_relevant_path(
        advisory_record.paths, commit.changed_files
    )
    commit_feature = CommitFeatures(
        commit=commit,
        references_vuln_id=references_vuln_id,
        time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
        changes_relevant_path=changes_relevant_path,
        commit_falls_in_given_interval_based_on_advisory_publicatation_date=commit_falls_in_given_interval_based_on_advisory_publicatation_date,
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


def extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
    commit_timestamp: int,
    advisory_record: AdvisoryRecord,
    days_before: int,
    days_after: int,
) -> bool:
    """
    Return True if the given commit falls in the given interval from advisory record publication date
    """
    timestamp = advisory_record.published_timestamp

    return extract_commit_in_given_interval(
        timestamp, commit_timestamp, -days_before
    ) or extract_commit_in_given_interval(timestamp, commit_timestamp, days_after)


def extract_commit_in_given_interval(
    version_timestamp: int, commit_timestamp: int, day_interval: int
) -> bool:
    """
    Return True if the commit is in the given interval before or after the timestamp
    """
    DAY_IN_SECONDS = 86400

    if day_interval == 0:
        return version_timestamp == commit_timestamp
    elif day_interval > 0:
        return (
            version_timestamp + day_interval * DAY_IN_SECONDS >= commit_timestamp
            and version_timestamp <= commit_timestamp
        )
    else:
        return (
            version_timestamp + day_interval * DAY_IN_SECONDS <= commit_timestamp
            and version_timestamp >= commit_timestamp
        )
