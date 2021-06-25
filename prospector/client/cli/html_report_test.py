import os
import os.path
from random import choice, choices, getrandbits, randint

from client.cli.html_report import report_as_html
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


def random_list_of_cve(max_count: int):
    return [
        f"CVE-{randint(10000, 99999)}-{randint(10, 99)}"
        for _ in range(randint(0, max_count))
    ]


def random_commit_hash():
    hash = getrandbits(128)
    print("hash value: %032x" % hash)
    return f"{hash:032x}"


def test_report_generation():
    candidates = []
    for _ in range(100):
        commit_with_feature = CommitWithFeatures(
            commit=Commit(
                commit_id=random_commit_hash(),
                repository=random_url(4),
                message=" ".join(random_list_of_strs(100)),
            ),
            references_vuln_id=random_bool(),
            references_ghissue=random_bool(),
            time_between_commit_and_advisory_record=randint(0, 42),
            changes_relevant_path=set(random_list_of_path(4, 42)),
            other_CVE_in_message=set(random_list_of_cve(42)),
            avg_hunk_size=randint(0, 42),
            n_hunks=randint(0, 42),
            n_changed_files=randint(0, 42),
            contains_jira_reference=random_bool(),
            referred_to_by_pages_linked_from_advisories=set(random_list_of_url(4, 42)),
            referred_to_by_nvd=set(random_list_of_url(4, 42)),
        )
        candidates.append(commit_with_feature)

    filename = "test_report.html"
    if os.path.isfile(filename):
        os.remove(filename)
    generated_report = report_as_html(candidates, filename)
    assert os.path.isfile(generated_report)
