from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures

DAYS_BEFORE = 180
DAYS_AFTER = 365
DAY_IN_SECONDS = 86400


def extract_features(commit: Commit, advisory_record: AdvisoryRecord) -> CommitFeatures:
    references_vuln_id = extract_references_vuln_id(commit, advisory_record)
    time_between_commit_and_advisory_record = (
        extract_time_between_commit_and_advisory_record(commit, advisory_record)
    )
    commit_falls_in_given_interval_based_on_advisory_publicatation_date = (
        extract_is_close_to_advisory_date(
            commit, advisory_record, DAYS_BEFORE, DAYS_AFTER
        )
    )
    changes_relevant_path = extract_changes_relevant_path(commit, advisory_record)
    references_ghissue = extract_references_ghissue(commit)
    contains_jira_reference = extract_contains_jira_reference(commit)
    commit_feature = CommitFeatures(
        commit=commit,
        references_vuln_id=references_vuln_id,
        time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
        changes_relevant_path=changes_relevant_path,
        commit_falls_in_given_interval_based_on_advisory_publicatation_date=commit_falls_in_given_interval_based_on_advisory_publicatation_date,
        references_ghissue=references_ghissue,
        contains_jira_reference=contains_jira_reference,
    )
    return commit_feature


def extract_references_vuln_id(commit: Commit, advisory_record: AdvisoryRecord) -> bool:
    return advisory_record.vulnerability_id in commit.cve_refs


def extract_time_between_commit_and_advisory_record(
    commit: Commit, advisory_record: AdvisoryRecord
) -> int:
    return commit.timestamp - advisory_record.published_timestamp


def extract_changes_relevant_path(
    commit: Commit, advisory_record: AdvisoryRecord
) -> bool:
    """
    Decides whether any of the changed paths (by a commit) are in the list
    of relevant paths (mentioned in the advisory record)
    """
    return any(
        [changed_path in advisory_record.paths for changed_path in commit.changed_files]
    )


def extract_is_close_to_advisory_date(
    commit: Commit,
    advisory_record: AdvisoryRecord,
    days_before: int,
    days_after: int,
) -> bool:
    """
    Return True if the given commit falls in the given interval from advisory record publication date
    """
    timestamp = advisory_record.published_timestamp

    return is_commit_in_given_interval(
        timestamp, commit.timestamp, -days_before
    ) or is_commit_in_given_interval(timestamp, commit.timestamp, days_after)


def is_commit_in_given_interval(
    version_timestamp: int, commit_timestamp: int, day_interval: int
) -> bool:
    """
    Return True if the commit is in the given interval before or after the timestamp
    """

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


def extract_references_ghissue(commit: Commit) -> bool:
    return len(commit.ghissue_refs) > 0


def extract_contains_jira_reference(commit: Commit) -> bool:
    return len(commit.jira_refs) > 0
