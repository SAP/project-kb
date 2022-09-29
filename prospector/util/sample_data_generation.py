import os
from random import choice, choices, getrandbits, randint

from stats.collection import StatisticCollection


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


CODE_TOKEN_CHARS = ("+", "-", "=", '"', "_", ".", "")


def random_list_of_code_token(max_count: int, max_length: int, min_count: int = 0):
    return [
        choice(CODE_TOKEN_CHARS)
        .join(random_list_of_strs(min_count=2, max_count=max_length))
        .replace(" ", "")
        for _ in range(randint(min_count, max_count))
    ]


def random_list_of_path(max_length: int, max_count: int):
    return [
        os.path.join(*random_list_of_strs(min_count=1, max_count=max_length))
        for _ in range(randint(0, max_count))
    ]


PROTOCOLS = ["http://", "https://"]
SUFFIX = [".hu", ".com", ".org", ".ru", ".fr", ".de"]


def random_url(max_length: int):
    if random_bool():
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
    else:
        return (
            choice(PROTOCOLS)
            + "github.com/FrontEndART/project-kb"
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
    _hash = getrandbits(128)
    return f"{_hash:032x}"


def random_hunk(start: int, stop: int):
    start = randint(start, stop)
    size = randint(start, stop)
    return start, start + size


def random_list_of_hunks(stop: int, max_count: int, start: int = 0):
    return [random_hunk(start=start, stop=stop) for _ in range(randint(0, max_count))]


def random_dict_of_jira_refs(max_count: int):
    return dict.fromkeys(
        [
            f"{choice(SAMPLES)}-{str(randint(0, 1000))}"
            for _ in range(randint(0, max_count))
        ],
        "",
    )


def random_dict_of_github_issue_ids(stop: int, max_count: int, start: int = 0):
    return dict.fromkeys(
        [str(randint(start, stop)) for _ in range(randint(0, max_count))], ""
    )


def random_version(max_length: int, max_size: int, min_size: int = 0):
    return ".".join([str(randint(min_size, max_size)) for _ in range(max_length)])


def random_list_of_version(
    max_count: int, max_length: int, max_size: int, min_size: int = 0
):
    return [random_version(max_length, max_size, min_size) for _ in range(max_count)]


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
