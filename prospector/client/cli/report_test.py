import os
import os.path
from random import randint

from client.cli.report import as_html, as_json
from datamodel.advisory import build_advisory_record
from datamodel.commit import Commit
from util.sample_data_generation import (  # random_list_of_url,
    random_commit_hash,
    random_dict_of_github_issue_ids,
    random_dict_of_jira_refs,
    random_dict_of_strs,
    random_list_of_cve,
    random_list_of_path,
    random_list_of_strs,
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
            hunks=randint(1, 50),
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

    advisory = build_advisory_record("CVE-2014-0050")

    if os.path.isfile("test_report.html"):
        os.remove("test_report.html")
    if os.path.isfile("test_report.json"):
        os.remove("test_report.json")
    html = as_html(
        candidates, advisory, "test_report.html", statistics=sample_statistics()
    )
    json = as_json(candidates, advisory, "test_report.json")

    assert os.path.isfile(html)
    assert os.path.isfile(json)
