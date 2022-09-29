import pandas
import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, make_from_raw_commit
from git.git import Git
from util.sample_data_generation import random_list_of_cve

from .helpers import (  # extract_features,
    extract_changed_relevant_paths,
    extract_commit_mentioned_in_linked_pages,
    extract_other_CVE_in_message,
    extract_path_similarities,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
    extract_time_between_commit_and_advisory_record,
    is_commit_in_given_interval,
    is_commit_reachable_from_given_tag,
)


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


# def test_extract_features(repository, requests_mock):
#     requests_mock.get(
#         "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62"
#     )
#     requests_mock.get(
#         "https://for.testing.purposes/containing_commit_id_in_text",
#         text="some text 7532d2fb0d6081a12c2a48ec854a81a8b718be62 blah",
#     )

#     repo = repository
#     commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
#     processed_commit = make_from_raw_commit(commit)

#     advisory_record = AdvisoryRecord(
#         vulnerability_id="CVE-2020-26258",
#         repository_url="https://github.com/apache/struts",
#         published_timestamp=1607532756,
#         references=[
#             "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62",
#             "https://for.testing.purposes/containing_commit_id_in_text",
#         ],
#         paths=["pom.xml"],
#     )

#     extracted_features = extract_features(processed_commit, advisory_record)

#     assert extracted_features.references_vuln_id is True
#     assert extracted_features.time_between_commit_and_advisory_record == 1000000
#     assert extracted_features.changes_relevant_path == [
#         "pom.xml",
#     ]
#     assert extracted_features.other_CVE_in_message == [
#         "CVE-2020-26259",
#     ]
#     assert extracted_features.referred_to_by_pages_linked_from_advisories == [
#         "https://for.testing.purposes/containing_commit_id_in_text",
#     ]
#     assert extracted_features.referred_to_by_nvd == [
#         "https://for.testing.purposes/reference/to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62",
#     ]


def test_extract_references_vuln_id():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=[
            "test_advisory_record",
            "another_advisory_record",
            "yet_another_advisory_record",
        ],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="test_advisory_record")
    result = extract_references_vuln_id(commit, advisory_record)
    assert result is True


def test_time_between_commit_and_advisory_record():
    commit = Commit(
        commit_id="test_commit", repository="test_repository", timestamp=142
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", published_timestamp=100
    )
    assert (
        extract_time_between_commit_and_advisory_record(commit, advisory_record) == 42
    )


@pytest.fixture
def paths():
    return [
        "fire-nation/zuko/lightning.png",
        "water-bending/katara/necklace.gif",
        "air-nomad/aang/littlefoot.jpg",
        "earth-kingdom/toph/metal.png",
    ]


@pytest.fixture
def sub_paths():
    return [
        "lightning.png",
        "zuko/lightning.png",
        "fire-nation/zuko",
        "water-bending",
    ]


class TestExtractChangedRelevantPaths:
    @staticmethod
    def test_sub_path_matching(paths, sub_paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=paths
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=sub_paths
        )

        matched_paths = {
            "fire-nation/zuko/lightning.png",
            "water-bending/katara/necklace.gif",
        }

        assert extract_changed_relevant_paths(commit, advisory_record) == matched_paths

    @staticmethod
    def test_same_path_only(paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=paths
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[:2]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set(paths[:2])

    @staticmethod
    def test_same_path_and_others(paths):
        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=[paths[0]],
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[:2]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == {
            paths[0],
        }

    @staticmethod
    def test_no_match(paths):
        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=paths[:1],
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths[2:]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()

    @staticmethod
    def test_empty_list(paths):
        commit = Commit(
            commit_id="test_commit", repository="test_repository", changed_files=[]
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=paths
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()

        commit = Commit(
            commit_id="test_commit",
            repository="test_repository",
            changed_files=paths,
        )
        advisory_record = AdvisoryRecord(
            vulnerability_id="test_advisory_record", paths=[]
        )
        assert extract_changed_relevant_paths(commit, advisory_record) == set()


def test_extract_other_CVE_in_message():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=["CVE-2021-29425", "CVE-2021-21251"],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2020-31284")
    assert extract_other_CVE_in_message(commit, advisory_record) == {
        "CVE-2021-29425": "",
        "CVE-2021-21251": "",
    }
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2021-29425")
    result = extract_other_CVE_in_message(commit, advisory_record)
    assert result == {"CVE-2021-21251": ""}


def test_is_commit_in_given_interval():
    assert is_commit_in_given_interval(1359961896, 1359961896, 0)
    assert is_commit_in_given_interval(1359961896, 1360047896, 1)
    assert is_commit_in_given_interval(1359961896, 1359875896, -1)
    assert not is_commit_in_given_interval(1359961896, 1359871896, -1)
    assert not is_commit_in_given_interval(1359961896, 1360051896, 1)


def test_extract_referred_to_by_nvd(repository):
    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        references=[
            "https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E",
            "https://other.com",
        ],
    )

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert extract_referred_to_by_nvd(commit, advisory_record) == {
        "https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E",
    }

    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert extract_referred_to_by_nvd(commit, advisory_record) == set()


def test_is_commit_reachable_from_given_tag(repository):

    repo = repository
    raw_commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
    commit = make_from_raw_commit(raw_commit)

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        paths=["pom.xml"],
        published_timestamp=1000000,
        versions=["STRUTS_2_1_3", "STRUTS_2_3_9"],
    )

    assert not is_commit_reachable_from_given_tag(
        commit, advisory_record, advisory_record.versions[0]
    )

    assert is_commit_reachable_from_given_tag(
        make_from_raw_commit(
            repo.get_commit("2e19fc6670a70c13c08a3ed0927abc7366308bb1")
        ),
        advisory_record,
        advisory_record.versions[1],
    )


def test_extract_extract_commit_mentioned_in_linked_pages(repository, requests_mock):
    requests_mock.get(
        "https://for.testing.purposes/containing_commit_id_in_text_2",
        text="some text r97993e3d78e1f5389b7b172ba9f308440830ce5 blah",
    )

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        references=["https://for.testing.purposes/containing_commit_id_in_text_2"],
    )

    advisory_record.analyze(fetch_references=True)

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert extract_commit_mentioned_in_linked_pages(commit, advisory_record) == 1

    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert extract_commit_mentioned_in_linked_pages(commit, advisory_record) == 0


# def test_extract_referred_to_by_pages_linked_from_advisories_wrong_url(repository):
#     advisory_record = AdvisoryRecord(
#         vulnerability_id="CVE-2020-26258",
#         references=["https://non-existing-url.com"],
#     )

#     commit = Commit(
#         commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
#         repository="test_repository",
#     )
#     assert not extract_commit_mentioned_in_linked_pages(
#         commit, advisory_record
#     )


def test_extract_path_similarities():
    keywords = [
        "TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato",
        "Bolin+Bumi+Ozai+Katara",
        "Jinora.Appa.Unalaq.Zaheer",
        "Naga.LinBeifong",
        "Sokka.Kya",
        "Bumi=Momo=Naga=Iroh",
        "Sokka_Unalaq",
        "Sokka.Iroh.Pabu",
        "LinBeifong=Zuko",
        "TenzinBolinSokka",
        "Korra-AsamiSato-Pabu-Iroh",
        "Mako.Naga",
        "Jinora=Bumi",
        "BolinAppaKuvira",
        "TophBeifongIroh",
        "Amon+Zuko+Unalaq",
    ]
    paths = [
        "Unalaq/Aang/Suyin Beifong",
        "Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer",
        "Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko",
        "Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi",
        "Momo",
        "Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq",
    ]
    commit = Commit(changed_files=paths)
    advisory = AdvisoryRecord(
        vulnerability_id=list(random_list_of_cve(max_count=1, min_count=1).keys())[0],
        keywords=keywords,
    )
    similarities: pandas.DataFrame = extract_path_similarities(commit, advisory)
    expected = (
        ",changed file,code token,jaccard,sorensen-dice,otsuka-ochiai,levenshtein,damerau-levenshtein,length diff,inverted normalized levenshtein,inverted normalized damerau-levenshtein\n"
        "0,Unalaq/Aang/Suyin Beifong,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.09090909090909091,0.16666666666666666,0.17677669529663687,8,8,4,0.19999999999999996,0.19999999999999996\n"
        "1,Unalaq/Aang/Suyin Beifong,Bolin+Bumi+Ozai+Katara,0.0,0.0,0.0,4,4,0,0.6,0.6\n"
        "2,Unalaq/Aang/Suyin Beifong,Jinora.Appa.Unalaq.Zaheer,0.14285714285714285,0.25,0.25,4,4,0,0.6,0.6\n"
        "3,Unalaq/Aang/Suyin Beifong,Naga.LinBeifong,0.16666666666666666,0.2857142857142857,0.2886751345948129,3,3,1,0.7,0.7\n"
        "4,Unalaq/Aang/Suyin Beifong,Sokka.Kya,0.0,0.0,0.0,4,4,2,0.6,0.6\n"
        "5,Unalaq/Aang/Suyin Beifong,Bumi=Momo=Naga=Iroh,0.0,0.0,0.0,4,4,0,0.6,0.6\n"
        "6,Unalaq/Aang/Suyin Beifong,Sokka_Unalaq,0.2,0.3333333333333333,0.35355339059327373,4,4,2,0.6,0.6\n"
        "7,Unalaq/Aang/Suyin Beifong,Sokka.Iroh.Pabu,0.0,0.0,0.0,4,4,1,0.6,0.6\n"
        "8,Unalaq/Aang/Suyin Beifong,LinBeifong=Zuko,0.16666666666666666,0.2857142857142857,0.2886751345948129,4,4,1,0.6,0.6\n"
        "9,Unalaq/Aang/Suyin Beifong,TenzinBolinSokka,0.0,0.0,0.0,4,4,1,0.6,0.6\n"
        "10,Unalaq/Aang/Suyin Beifong,Korra-AsamiSato-Pabu-Iroh,0.0,0.0,0.0,5,5,1,0.5,0.5\n"
        "11,Unalaq/Aang/Suyin Beifong,Mako.Naga,0.0,0.0,0.0,4,4,2,0.6,0.6\n"
        "12,Unalaq/Aang/Suyin Beifong,Jinora=Bumi,0.0,0.0,0.0,4,4,2,0.6,0.6\n"
        "13,Unalaq/Aang/Suyin Beifong,BolinAppaKuvira,0.0,0.0,0.0,4,4,1,0.6,0.6\n"
        "14,Unalaq/Aang/Suyin Beifong,TophBeifongIroh,0.16666666666666666,0.2857142857142857,0.2886751345948129,4,4,1,0.6,0.6\n"
        "15,Unalaq/Aang/Suyin Beifong,Amon+Zuko+Unalaq,0.16666666666666666,0.2857142857142857,0.2886751345948129,4,4,1,0.6,0.6\n"
        "16,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.25,0.4,0.4008918628686366,8,8,0,0.19999999999999996,0.19999999999999996\n"
        "17,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Bolin+Bumi+Ozai+Katara,0.1,0.18181818181818182,0.1889822365046136,8,8,4,0.19999999999999996,0.19999999999999996\n"
        "18,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Jinora.Appa.Unalaq.Zaheer,0.1,0.18181818181818182,0.1889822365046136,7,7,4,0.30000000000000004,0.30000000000000004\n"
        "19,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Naga.LinBeifong,0.1111111111111111,0.2,0.2182178902359924,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "20,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Sokka.Kya,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "21,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Bumi=Momo=Naga=Iroh,0.1,0.18181818181818182,0.1889822365046136,8,8,4,0.19999999999999996,0.19999999999999996\n"
        "22,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Sokka_Unalaq,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "23,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Sokka.Iroh.Pabu,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "24,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,LinBeifong=Zuko,0.1111111111111111,0.2,0.2182178902359924,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "25,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,TenzinBolinSokka,0.1111111111111111,0.2,0.2182178902359924,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "26,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Korra-AsamiSato-Pabu-Iroh,0.2,0.3333333333333333,0.3380617018914066,6,6,3,0.4,0.4\n"
        "27,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Mako.Naga,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "28,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Jinora=Bumi,0.125,0.2222222222222222,0.2672612419124244,7,7,6,0.30000000000000004,0.30000000000000004\n"
        "29,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,BolinAppaKuvira,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "30,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,TophBeifongIroh,0.1111111111111111,0.2,0.2182178902359924,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "31,Tenzin/Asami Sato/Suyin Beifong/Tenzin/Bumi/Zaheer,Amon+Zuko+Unalaq,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "32,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.23076923076923078,0.375,0.375,8,8,0,0.19999999999999996,0.19999999999999996\n"
        "33,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Bolin+Bumi+Ozai+Katara,0.09090909090909091,0.16666666666666666,0.17677669529663687,7,7,4,0.30000000000000004,0.30000000000000004\n"
        "34,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Jinora.Appa.Unalaq.Zaheer,0.0,0.0,0.0,8,8,4,0.19999999999999996,0.19999999999999996\n"
        "35,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Naga.LinBeifong,0.1,0.18181818181818182,0.20412414523193154,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "36,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Sokka.Kya,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "37,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Bumi=Momo=Naga=Iroh,0.09090909090909091,0.16666666666666666,0.17677669529663687,7,7,4,0.30000000000000004,0.30000000000000004\n"
        "38,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Sokka_Unalaq,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "39,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Sokka.Iroh.Pabu,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "40,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,LinBeifong=Zuko,0.1,0.18181818181818182,0.20412414523193154,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "41,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,TenzinBolinSokka,0.1,0.18181818181818182,0.20412414523193154,7,7,5,0.30000000000000004,0.30000000000000004\n"
        "42,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Korra-AsamiSato-Pabu-Iroh,0.18181818181818182,0.3076923076923077,0.31622776601683794,7,7,3,0.30000000000000004,0.30000000000000004\n"
        "43,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Mako.Naga,0.1111111111111111,0.2,0.25,7,7,6,0.30000000000000004,0.30000000000000004\n"
        "44,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Jinora=Bumi,0.0,0.0,0.0,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "45,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,BolinAppaKuvira,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "46,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,TophBeifongIroh,0.0,0.0,0.0,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "47,Asami Sato/Tenzin/Tonraq/Katara/Tarrlok/Naga/Zuko,Amon+Zuko+Unalaq,0.1,0.18181818181818182,0.20412414523193154,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "48,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.3333333333333333,0.5,0.5,9,9,1,0.09999999999999998,0.09999999999999998\n"
        "49,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Bolin+Bumi+Ozai+Katara,0.2,0.3333333333333333,0.35355339059327373,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "50,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Jinora.Appa.Unalaq.Zaheer,0.0,0.0,0.0,9,9,5,0.09999999999999998,0.09999999999999998\n"
        "51,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Naga.LinBeifong,0.1,0.18181818181818182,0.20412414523193154,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "52,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Sokka.Kya,0.0,0.0,0.0,9,9,7,0.09999999999999998,0.09999999999999998\n"
        "53,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Bumi=Momo=Naga=Iroh,0.09090909090909091,0.16666666666666666,0.17677669529663687,8,8,5,0.19999999999999996,0.19999999999999996\n"
        "54,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Sokka_Unalaq,0.0,0.0,0.0,9,9,7,0.09999999999999998,0.09999999999999998\n"
        "55,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Sokka.Iroh.Pabu,0.0,0.0,0.0,9,9,6,0.09999999999999998,0.09999999999999998\n"
        "56,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,LinBeifong=Zuko,0.1,0.18181818181818182,0.20412414523193154,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "57,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,TenzinBolinSokka,0.1,0.18181818181818182,0.20412414523193154,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "58,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Korra-AsamiSato-Pabu-Iroh,0.18181818181818182,0.3076923076923077,0.31622776601683794,7,7,4,0.30000000000000004,0.30000000000000004\n"
        "59,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Mako.Naga,0.0,0.0,0.0,9,9,7,0.09999999999999998,0.09999999999999998\n"
        "60,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Jinora=Bumi,0.1111111111111111,0.2,0.25,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "61,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,BolinAppaKuvira,0.2222222222222222,0.36363636363636365,0.4082482904638631,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "62,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,TophBeifongIroh,0.2222222222222222,0.36363636363636365,0.4082482904638631,7,7,6,0.30000000000000004,0.30000000000000004\n"
        "63,Amon/Asami Sato/Bumi/Kuvira/Toph Beifong/Bolin/Bumi,Amon+Zuko+Unalaq,0.1,0.18181818181818182,0.20412414523193154,8,8,6,0.19999999999999996,0.19999999999999996\n"
        "64,Momo,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.0,0.0,0.0,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "65,Momo,Bolin+Bumi+Ozai+Katara,0.0,0.0,0.0,4,4,3,0.6,0.6\n"
        "66,Momo,Jinora.Appa.Unalaq.Zaheer,0.0,0.0,0.0,4,4,3,0.6,0.6\n"
        "67,Momo,Naga.LinBeifong,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "68,Momo,Sokka.Kya,0.0,0.0,0.0,2,2,1,0.8,0.8\n"
        "69,Momo,Bumi=Momo=Naga=Iroh,0.25,0.4,0.5,3,3,3,0.7,0.7\n"
        "70,Momo,Sokka_Unalaq,0.0,0.0,0.0,2,2,1,0.8,0.8\n"
        "71,Momo,Sokka.Iroh.Pabu,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "72,Momo,LinBeifong=Zuko,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "73,Momo,TenzinBolinSokka,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "74,Momo,Korra-AsamiSato-Pabu-Iroh,0.0,0.0,0.0,5,5,4,0.5,0.5\n"
        "75,Momo,Mako.Naga,0.0,0.0,0.0,2,2,1,0.8,0.8\n"
        "76,Momo,Jinora=Bumi,0.0,0.0,0.0,2,2,1,0.8,0.8\n"
        "77,Momo,BolinAppaKuvira,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "78,Momo,TophBeifongIroh,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "79,Momo,Amon+Zuko+Unalaq,0.0,0.0,0.0,3,3,2,0.7,0.7\n"
        "80,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,TophBeifong_Zuko_IknikBlackstoneVarrick_AsamiSato,0.13333333333333333,0.23529411764705882,0.23570226039551587,9,9,2,0.09999999999999998,0.09999999999999998\n"
        "81,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Bolin+Bumi+Ozai+Katara,0.08333333333333333,0.15384615384615385,0.16666666666666666,9,9,6,0.09999999999999998,0.09999999999999998\n"
        "82,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Jinora.Appa.Unalaq.Zaheer,0.08333333333333333,0.15384615384615385,0.16666666666666666,10,10,6,0.0,0.0\n"
        "83,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Naga.LinBeifong,0.2,0.3333333333333333,0.3849001794597505,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "84,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Sokka.Kya,0.1,0.18181818181818182,0.23570226039551587,9,9,8,0.09999999999999998,0.09999999999999998\n"
        "85,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Bumi=Momo=Naga=Iroh,0.0,0.0,0.0,10,10,6,0.0,0.0\n"
        "86,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Sokka_Unalaq,0.2222222222222222,0.36363636363636365,0.47140452079103173,8,8,8,0.19999999999999996,0.19999999999999996\n"
        "87,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Sokka.Iroh.Pabu,0.09090909090909091,0.16666666666666666,0.19245008972987526,9,9,7,0.09999999999999998,0.09999999999999998\n"
        "88,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,LinBeifong=Zuko,0.2,0.3333333333333333,0.3849001794597505,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "89,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,TenzinBolinSokka,0.2,0.3333333333333333,0.3849001794597505,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "90,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Korra-AsamiSato-Pabu-Iroh,0.07692307692307693,0.14285714285714285,0.14907119849998599,10,10,5,0.0,0.0\n"
        "91,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Mako.Naga,0.1,0.18181818181818182,0.23570226039551587,9,9,8,0.09999999999999998,0.09999999999999998\n"
        "92,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Jinora=Bumi,0.0,0.0,0.0,10,10,8,0.0,0.0\n"
        "93,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,BolinAppaKuvira,0.2,0.3333333333333333,0.3849001794597505,9,9,7,0.09999999999999998,0.09999999999999998\n"
        "94,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,TophBeifongIroh,0.2,0.3333333333333333,0.3849001794597505,8,8,7,0.19999999999999996,0.19999999999999996\n"
        "95,Kuvira/Bolin/Lin Beifong/Sokka/Mako/Korra/Toph Beifong/Unalaq,Amon+Zuko+Unalaq,0.09090909090909091,0.16666666666666666,0.19245008972987526,9,9,7,0.09999999999999998,0.09999999999999998\n"
    )

    assert similarities.to_csv() == expected
