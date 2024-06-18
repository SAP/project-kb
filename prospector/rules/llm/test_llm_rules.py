from typing import List

import pytest

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from rules.nlp.nlp_phase import NLPPhase

# from datamodel.commit_features import CommitWithFeatures


@pytest.fixture
def candidates():
    return [
        Commit(
            repository="repo1",
            commit_id="1",
            message="Blah blah blah fixes CVE-2020-26258 and a few other issues",
            ghissue_refs={"example": ""},
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            cve_refs=["CVE-2020-26258"],
        ),
        Commit(repository="repo2", commit_id="2", cve_refs=["CVE-2020-26258"]),
        Commit(
            repository="repo3",
            commit_id="3",
            message="Another commit that fixes CVE-2020-26258",
            ghissue_refs={"example": ""},
        ),
        Commit(
            repository="repo4",
            commit_id="4",
            message="Endless loop causes DoS vulnerability",
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
        ),
        Commit(
            repository="repo5",
            commit_id="7532d2fb0d6081a12c2a48ec854a81a8b718be62",
            message="Insecure deserialization",
            changed_files={
                "core/src/main/java/org/apache/cxf/workqueue/AutomaticWorkQueueImpl.java"
            },
        ),
    ]


@pytest.fixture
def advisory_record():
    return AdvisoryRecord(
        cve_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references=["https://reference.to/some/commit/7532d2fb0d60", 1],
        keywords=["AutomaticWorkQueueImpl"],
        # paths=["pom.xml"],
    )


def test_many_aspects():
    print("TODO")
