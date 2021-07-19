import os
import os.path
from random import choice, choices, getrandbits, randint

from client.cli.html_report import report_as_html
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures


def random_bool():
    return choice([True, False])


SAMPLES = [
    "Aang",
    "Appa",
    "Azula",
    "Iroh",
    "Katara",
    "Momo",
    "Ozai",
    "Sokka",
    "Toph Beifong",
    "Zuko",
    "Amon",
    "Asami Sato",
    "Bolin",
    "Bumi",
    "Iknik Blackstone Varrick",
    "Jinora",
    "Korra",
    "Kuvira",
    "Kya",
    "Lin Beifong",
    "Mako",
    "Naga",
    "Pabu",
    "Suyin Beifong",
    "Tarrlok",
    "Tenzin",
    "Tonraq",
    "Unalaq",
    "Zaheer",
]


def random_list_of_strs(max_count: int, min_count: int = 0):
    return choices(SAMPLES, k=randint(min_count, max_count))


def random_dict_of_strs(max_count: int, max_length: int, min_count: int = 0):
    return {
        choice(SAMPLES): " ".join(
            random_list_of_strs(min_count=1, max_count=max_length)
        )
        for _ in range(randint(min_count, max_count))
    }


def random_list_of_path(max_length: int, max_count: int):
    return [
        os.path.join(*random_list_of_strs(min_count=1, max_count=max_length))
        for _ in range(randint(0, max_count))
    ]


PROTOCOLS = ["http://", "https://"]
SUFFIX = [".hu", ".com", ".org", ".ru", ".fr", ".de"]


def random_url(max_length: int):
    return (
        choice(PROTOCOLS)
        + "/".join(
            map(
                lambda s: s.lower().replace(" ", "-"),
                random_list_of_strs(min_count=1, max_count=max_length),
            )
        )
        + choice(SUFFIX)
    )


def random_list_of_url(max_length: int, max_count: int):
    return [random_url(max_length) for _ in range(randint(0, max_count))]


def random_list_of_cve(max_count: int, min_count: int = 0):
    return [
        f"CVE-{randint(1987, 2021)}-{str(randint(10, 99)).rjust(4, '0')}"
        for _ in range(randint(min_count, max_count))
    ]


def random_commit_hash():
    hash = getrandbits(128)
    print("hash value: %032x" % hash)
    return f"{hash:032x}"


def random_hunk(start: int, stop: int):
    start = randint(start, stop)
    size = randint(start, stop)
    return (start, start + size)


def random_list_of_hunks(stop: int, max_count: int, start: int = 0):
    return [random_hunk(start=start, stop=stop) for _ in range(randint(0, max_count))]


def random_list_of_jira_refs(max_count: int):
    return [
        f"{choice(SAMPLES)}-{str(randint(0, 1000))}"
        for _ in range(randint(0, max_count))
    ]


def random_list_of_github_issue_ids(stop: int, max_count: int, start: int = 0):
    return [str(randint(start, stop)) for _ in range(randint(0, max_count))]


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

    filename = "test_report.html"
    if os.path.isfile(filename):
        os.remove(filename)
    generated_report = report_as_html(
        candidates,
        AdvisoryRecord(
            vulnerability_id=random_list_of_cve(max_count=1, min_count=1)[0]
        ),
        filename,
    )
    assert os.path.isfile(generated_report)
