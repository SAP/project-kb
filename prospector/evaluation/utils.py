import csv
import re
from datamodel.advisory import build_advisory_record
from urllib.parse import urlparse


VULN = ["version", "through", "versions"]

FIXED = [
    "before",
    "before release",
    "before version",
    "prior to",
    "upgrade to",
    "fixed in",
    "fixed in version",
    "fixed in release",
    "to version",
]


def load_dataset(path: str):
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        return [row for row in reader if "CVE" in row[0] and row[3] != "True"]


def is_real_version(text: str):
    return bool(re.match(r"\d+\.(?:\d+\.*)*\d", text))


def get_version_spacy(text: str, nlp):
    """This function extracts vulnerable and fixed version numbers from a given text using spaCy."""
    doc = nlp(text)
    # relevant_sentences = {}
    # relevant_sentence = ""
    fixed_version = ""
    vulnerable_version = ""
    for i in range(len(doc))[1:]:
        if is_real_version(doc[i].text):
            if doc[i - 1].text in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (doc[i - 2].text + " " + doc[i - 1].text) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (
                doc[i - 3].text + " " + doc[i - 2].text + " " + doc[i - 1].text
            ) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            else:
                # relevant_sentence = doc[: i + 1]
                vulnerable_version = doc[i].text
    return vulnerable_version, fixed_version


def check_advisory(cve, repository=None, nlp=None):
    """This function checks the advisory for a given CVE and attempts to extract version information."""
    advisory = build_advisory_record(
        cve, nvd_rest_endpoint="http://localhost:8000/nvd/vulnerabilities/"
    )
    references = [urlparse(r).netloc for r in advisory.references]
    return references
    vuln = "None"
    if len(advisory.versions.get("affected")):
        vuln = advisory.versions.get("affected")[-1]

    fixed = "None"
    if len(advisory.versions.get("fixed")):
        fixed = advisory.versions.get("fixed")[-1]

    vuln2, fixed2 = get_version_spacy(advisory.description, nlp)
    res = [advisory.cve_id, advisory.description]
    if fixed == fixed2 and vuln == vuln2:
        res.append(f"{vuln}:{fixed}")
    if fixed == "None" and fixed2 != "":
        res.append(f"{vuln}:{fixed2}")
    if vuln == "None" and vuln2 != "":
        res.append(f"{vuln2}:{fixed}")
    if fixed != fixed2 and fixed2 != "" and fixed != "None":
        res.append(f"{vuln}:{fixed}")
        res.append(f"{vuln}:{fixed2}")

    if len(res) > 2:
        res.append("***************************************")
        print(advisory.cve_id)
        return res
    else:
        res.append(f"{vuln}:{fixed}")
        res.append("***************************************")
        print(advisory.cve_id)
        return res
