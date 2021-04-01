from main import advisory_record_to_output
from datamodel.advisory import AdvisoryRecord

import re
import requests

NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cve/1.0/"


class AdvisoryProcessor:
    """
    An instance of this class is used to parse an advisory
    and construct an AdvisoryRecord object.
    This works both with NVD advisories and other textual descriptions.
    """

    # advisory_record: AdvisoryRecord = None

    def __init__(self) -> None:
        pass

    def process(self, ar: AdvisoryRecord) -> AdvisoryRecord:
        """Fills-in the missing content of an AdvisoryRecord object

        Args:
            ar(AdvisoryRecord): an AdvisoryRecord with at least a vuln-id

        Returns:
            AdvisoryRecord: a record with all the relevant fields filled-in
        """
        # self.advisory_record = AdvisoryRecord(
        #     vulnerability_id, "", vulnerability_description=advisory_text
        # )

        self.advisory_record = ar

        if self.advisory_record.vulnerability_description == "":
            self.advisory_record = getFromNVD(self.advisory_record.vulnerability_id)

        self.advisory_record.versions = extract_versions(
            self.advisory_record.vulnerability_description
        )

        # TODO implement advisory parsing
        # ........
        # do the actual processing, maybe using spacy
        # .......

        return self.advisory_record


def extract_versions(text) -> "list[str]":
    """
    Extract all versions mentioned in the advisory text
    """
    regex = r"[0-9]{1,}\.[0-9]{1,}[0-9a-z.]*"
    result = re.findall(regex, text)

    return result


def extract_products(text) -> "list[str]":
    """
    Extract product names from advisory text
    """
    # TODO implement this
    return []


def getFromNVD(vuln_id: str):
    """
    populate object field using NVD data
    """
    ar = AdvisoryRecord(vuln_id, "")

    try:
        response = requests.get(NVD_REST_ENDPOINT + vuln_id)
        if response.status_code != 200:
            return ar
        data = response.json()["result"]["CVE_Items"][0]
        ar.published_timestamp = data["publishedDate"]
        ar.last_modified_timestamp = data["lastModifiedDate"]
        ar.vulnerability_description = data["cve"]["description"]["description_data"][
            0
        ]["value"]
        ar.references = [r["url"] for r in data["cve"]["references"]["reference_data"]]

    except:
        print("Could not retrieve vulnerability data from NVD for " + vuln_id)

    return ar
