# from dataclasses import asdict
# import pytest
# import spacy
from spacy.lang.en import English

from datamodel.advisory import AdvisoryRecord

ADVISORY_TEXT_1 = """Unspecified vulnerability in Uconnect before 15.26.1, as used
    in certain Fiat Chrysler Automobiles (FCA) from 2013 to 2015 models, allows
    remote attackers in the same cellular network to control vehicle movement,
    cause human harm or physical damage, or modify dashboard settings via
    vectors related to modification of entertainment-system firmware and access
    of the CAN bus due to insufficient \\"Radio security protection,\\" as
    demonstrated on a 2014 Jeep Cherokee Limited FWD."""

ADVISORY_TEXT_2 = """
In Apache Commons IO before 2.7, When invoking the method FileNameUtils.normalize
with an improper input string, like "//../foo", or "\\..\\foo", the result would be
the same value, thus possibly providing access to files in the parent directory,
but not further above (thus "limited" path traversal), if the calling code would
use the result to construct a path value."""

ADVISORY_TEXT_3 = """
Apache Commons BeanUtils, as distributed in lib/commons-beanutils-1.8.0.jar in
Apache Struts 1.x through 1.3.10 and in other products requiring
commons-beanutils through 1.9.2, does not suppress the class property, which
allows remote attackers to "manipulate" the ClassLoader and execute arbitrary
code via the class parameter, as demonstrated by the passing of this parameter
to the getClass method of the ActionForm object in Struts 1.
"""


ADVISORIES = [ADVISORY_TEXT_1, ADVISORY_TEXT_2, ADVISORY_TEXT_3]


def test_advisory_basic():
    adv_rec = AdvisoryRecord(
        vulnerability_id="CVE-2015-5612",
        repository_url="https://github.com/abc/xyz",
        references=[
            "https://github.com/abc/def/commit/af542817cb325173410876aa3",
            "https://github.com/abc/def/issues/54",
        ],
    )

    assert adv_rec.repository_url == "https://github.com/abc/xyz"

    mentions_commit = False
    for r in adv_rec.references:
        if "af542817c" in r:
            mentions_commit = True

    assert mentions_commit
    # assert ar.vulnerability_id == "CVE-2015-5612"
    # assert ar.published_timestamp == "2015-09-04T15:59Z"


def test_adv_record_versions():

    record = AdvisoryRecord(
        vulnerability_id="CVE-2014-0050", description=ADVISORY_TEXT_1
    )
    record.analyze()

    assert "15.26.1" in record.versions
    assert "15.26" not in record.versions


# def test_adv_record_nvd():
#     record = AdvisoryRecord(vulnerability_id="CVE-2014-0050")

#     record.analyze(use_nvd=True)

#     # print(record)
#     assert "1.3.1" in record.versions
#     assert "1.3" not in record.versions


def test_adv_record_products():
    record = AdvisoryRecord(
        vulnerability_id="CVE-XXXX-YYYY", description=ADVISORY_TEXT_1
    )
    record.analyze()

    # print(record)
    assert "Chrysler" in record.affected_products


def test_adv_record_keywords():
    record = AdvisoryRecord(
        vulnerability_id="CVE-XXXX-YYYY", description=ADVISORY_TEXT_2
    )
    record.analyze()

    assert record.keywords == (
        "IO",
        "2.7,",
        "FileNameUtils.normalize",
        '"//../foo",',
        '"\\..\\foo",',
        '"limited"',
    )


def test_process_description_spacy():
    # see https://spacy.io/usage/rule-based-matching#entityruler

    nlp = English()
    nlp.add_pipe("entity_ruler").from_disk("./datamodel/gazetteers/products.jsonl")

    for adv in ADVISORIES:
        product_names = []
        doc = nlp(adv)
        # for token in doc:
        #     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,  token.shape_, token.is_alpha, token.is_stop)

        for entity in doc.ents:
            if entity.label_ == "PROD":
                product_names.append(entity.text)

        print(product_names)

    return product_names
