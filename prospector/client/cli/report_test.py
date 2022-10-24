import os
import os.path
from random import randint

from client.cli.report import as_html, as_json, report_on_console
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from util.sample_data_generation import (  # random_list_of_url,
    random_bool,
    random_commit_hash,
    random_dict_of_strs,
    random_list_of_cve,
    random_dict_of_github_issue_ids,
    random_list_of_hunks,
    random_dict_of_jira_refs,
    random_list_of_path,
    random_list_of_strs,
    random_list_of_version,
    random_url,
    sample_statistics,
)


def test_report_generation():
    candidates = []
    for _ in range(100):
        annotated_candidates = Commit(
            commit_id=random_commit_hash(),
            repository=random_url(4),
            message=" ".join(random_list_of_strs(100)),
            timestamp=randint(0, 100000),
            hunks=random_list_of_hunks(1000, 42),
            diff=random_list_of_strs(200),
            changed_files=random_list_of_path(4, 42),
            message_reference_content=random_list_of_strs(42),
            jira_refs=random_dict_of_jira_refs(42),
            ghissue_refs=random_dict_of_github_issue_ids(100000, 42),
            cve_refs=random_list_of_cve(42),
            tags=random_list_of_strs(42),
            annotations=random_dict_of_strs(16, 10),
        )

        candidates.append(annotated_candidates)

    advisory = AdvisoryRecord(
        vulnerability_id=random_list_of_cve(max_count=1, min_count=1)[0],
        repository_url=random_url(4),
        published_timestamp=randint(0, 100000),
        last_modified_timestamp=randint(0, 100000),
        references=random_list_of_strs(42),
        references_content=random_list_of_strs(42),
        affected_products=random_list_of_strs(42),
        description=" ".join(random_list_of_strs(42)),
        preprocessed_vulnerability_description=" ".join(random_list_of_strs(42)),
        relevant_tags=random_list_of_strs(42),
        versions=random_list_of_version(42, 4, 42),
        from_nvd=random_bool(),
        paths=random_list_of_path(4, 42),
        keywords=tuple(random_list_of_strs(42)),
    )

    filename = "test_report.html"
    if os.path.isfile(filename):
        os.remove(filename)
    generated_report = as_html(
        candidates, advisory, filename, statistics=sample_statistics()
    )
    assert os.path.isfile(generated_report)
