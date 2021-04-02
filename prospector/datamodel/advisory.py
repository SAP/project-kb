import re
import requests

from dataclasses import dataclass, field

# from . import BaseModel

NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cve/1.0/"


@dataclass
class AdvisoryRecord:
    """
    The advisory record captures all relevant information on the vulnerability advisory
    """

    vulnerability_id: str
    repository_url: str = ""
    published_timestamp: str = ""
    last_modified_timestamp: str = ""
    references: "list[str]" = field(default_factory=list)
    references_content: "list[str]" = field(default_factory=list)
    advisory_references: "list[str]" = field(default_factory=list)
    vulnerability_description: str = ""
    preprocessed_vulnerability_description: str = ""
    relevant_tags: "list[str]" = None
    versions: "list[str]" = field(default_factory=list)

    # """
    # Information to provide when initializing an advisory record
    # Input:
    #     vulnerability_id (str): the vulnerability ID, typically a CVE
    #     published_timestamp (str/int): the timestamp at which the vulnerability was published, or patched if that is known
    #     repo_url (str): the URL of the affected (GitHub) repository URL
    #     nvd_references (list): references to which the NVD refers (1st level references)
    #     references_content (str): the content that was extracted from these references, and will be used to compare lexical similarity with
    #     advisory_references (list): the references that were extracted from the NVD references (2nd level references)
    #     vulnerability_description (str): the vulnerability description
    #     connection (sqlite3.connection): the connection with the (commits) database
    #     Optional:
    #         preprocessed_vulnerability_description (str): if there is already a preprocess vulnerability description
    #         relevant_tags (list): a list of tags that are regarded as relevant tags (affected versions of the software)
    #         verbose (bool): to print intermediate output
    #         since (timestamp): lower bound for selecting the candidate commits
    #         until (timestamp): upper bound for selecting the candidate commits
    # """
    # self.id = vulnerability_id
    # self.published_timestamp = published_timestamp
    # self.repo_url = re.sub("\.git$|/$", "", repo_url)
    # self.is_github_url = "https://github.com" in repo_url
    # self.project_name = extract_project_name_from_repository_url(self.repo_url)
    # self.description = vulnerability_description
    # self.relevant_tags = relevant_tags

    # if preprocessed_vulnerability_description == None:
    #     self.preprocessed_description = simpler_filter_text(
    #         vulnerability_description
    #     )
    # else:
    #     self.preprocessed_description = preprocessed_vulnerability_description

    # # self.git_repo = Git(repo_url, cache_path=GIT_CACHE)
    # # self.git_repo.clone(skip_existing=True)  # @TODO: true or false..?

    # self.references = references
    # self.references_content = references_content


# TODO convert into a constructor for AdvisoryRecord
def buildAdvisoryRecord(
    vuln_id: str, vuln_description: str = "", query_nvd: bool = False
) -> AdvisoryRecord:
    """
    Creates an instance of AdvisoryRecord

    Args:
        ar(AdvisoryRecord): an AdvisoryRecord with at least a vuln-id

    Returns:
        AdvisoryRecord: a record with all the relevant fields filled-in
    """

    adv_rec = AdvisoryRecord(vuln_id)

    if query_nvd:
        adv_rec = getFromNVD(vuln_id)

    adv_rec.vulnerability_description += vuln_description

    # start annotating/pre-processing
    adv_rec.versions = extract_versions(adv_rec.vulnerability_description)

    return adv_rec


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
    # TODO implement this properly
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


@dataclass
class Reference:
    """
    Used for analyzing the references
    """

    url: str
    repo_url: str

    def __post_init__(self):
        # TODO this is not general (the .git suffix can be stripped only for github)
        self.repo_url = re.sub(r"\.git$|/$", "", self.repo_url)

    def is_pull_page(self):
        return self.repo_url + "/pull/" in self.url

    def is_issue_page(self):
        return self.repo_url + "/issues/" in self.url

    def is_tag_page(self):
        return self.repo_url + "/releases/tag/" in self.url

    def is_commit_page(self):
        return self.repo_url + "/commit/" in self.url
