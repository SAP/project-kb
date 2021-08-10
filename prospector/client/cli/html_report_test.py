import os
import os.path
from random import randint

from client.cli.html_report import report_as_html
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures
from simple_hierarchical_storage.collection import StatisticCollection
from util.sample_data_generation import (
    random_bool,
    random_commit_hash,
    random_dict_of_strs,
    random_list_of_cve,
    random_list_of_github_issue_ids,
    random_list_of_hunks,
    random_list_of_jira_refs,
    random_list_of_path,
    random_list_of_strs,
    random_list_of_url,
    random_list_of_version,
    random_url,
)


def sample_statistics():
    stats = StatisticCollection()
    stats.record("apple time", 12)
    stats.record("grape", 84)
    stats.record(("lemon", "space time"), 42, unit="cochren")
    stats.record(("lemon", "grape"), 128, unit="pezeta")
    stats.collect(("lemon", "zest"), 1, unit="pinch")
    stats.collect(("lemon", "zest"), 3)
    stats.collect(("lemon", "zest"), 12)
    stats.collect(("lemon", "zest"), 56)
    stats.collect(("melon", "marry"), 34)
    stats.collect(("melon", "marry"), 34.12)
    stats.collect(("melon", "sweet"), 27)
    stats.collect(("melon", "sweet"), 27.23)
    stats.collect(("melon", "sweet"), 0.27)
    stats.collect(("melon", "sweet"), 2.3)

    return stats


def test_report_generation():
    candidates = []
    for _ in range(100):
        commit_with_feature = CommitWithFeatures(
            commit=Commit(
                commit_id=random_commit_hash(),
                repository=random_url(4),
                message=" ".join(random_list_of_strs(100)),
                timestamp=randint(0, 100000),
                hunks=random_list_of_hunks(1000, 42),
                diff=random_list_of_strs(200),
                changed_files=random_list_of_path(4, 42),
                message_reference_content=random_list_of_strs(42),
                jira_refs=random_list_of_jira_refs(42),
                ghissue_refs=random_list_of_github_issue_ids(100000, 42),
                cve_refs=random_list_of_cve(42),
                tags=random_list_of_strs(42),
            ),
            references_vuln_id=random_bool(),
            time_between_commit_and_advisory_record=randint(0, 42),
            changes_relevant_path=set(random_list_of_path(4, 42)),
            other_CVE_in_message=set(random_list_of_cve(42)),
            referred_to_by_pages_linked_from_advisories=set(random_list_of_url(4, 42)),
            referred_to_by_nvd=set(random_list_of_url(4, 42)),
            annotations=random_dict_of_strs(16, 10),
        )
        candidates.append(commit_with_feature)

    advisory = AdvisoryRecord(
        vulnerability_id=random_list_of_cve(max_count=1, min_count=1)[0],
        repository_url=random_url(4),
        published_timestamp=randint(0, 100000),
        last_modified_timestamp=randint(0, 100000),
        references=random_list_of_strs(42),
        references_content=random_list_of_strs(42),
        advisory_references=random_list_of_cve(42),
        affected_products=random_list_of_strs(42),
        description=" ".join(random_list_of_strs(42)),
        preprocessed_vulnerability_description=" ".join(random_list_of_strs(42)),
        relevant_tags=random_list_of_strs(42),
        versions=random_list_of_version(42, 4, 42),
        from_nvd=random_bool(),
        paths=random_list_of_path(4, 42),
        code_tokens=tuple(random_list_of_strs(42)),
    )

    filename = "test_report.html"
    if os.path.isfile(filename):
        os.remove(filename)
    generated_report = report_as_html(
        candidates, advisory, filename, statistics=sample_statistics()
    )
    assert os.path.isfile(generated_report)
