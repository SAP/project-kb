# from typing import Tuple
import re
from dataclasses import dataclass, field

import requests

from commit_preprocessor.constants import RELEVANT_EXTENSIONS

# from . import BaseModel

# TODO use prospector own NVD feed endpoint
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
    affected_products: "list[str]" = field(default_factory=list)
    description: str = ""
    preprocessed_vulnerability_description: str = ""
    relevant_tags: "list[str]" = None
    versions: "list[str]" = field(default_factory=list)
    from_nvd: bool = False
    nvd_rest_endpoint: str = NVD_REST_ENDPOINT
    paths: "list[str]" = field(default_factory=list)

    def __post_init__(self):
        if self.from_nvd:
            self._get_from_nvd(self.vulnerability_id, self.nvd_rest_endpoint)

        self.versions.extend(
            [v for v in extract_versions(self.description) if v not in self.versions]
        )
        self.affected_products = extract_products(self.description)
        self.paths = extract_path_tokens(self.description)

    def _get_from_nvd(self, vuln_id: str, nvd_rest_endpoint: str = NVD_REST_ENDPOINT):
        """
        populate object field using NVD data
        returns: description, published_timestamp, last_modified timestamp, list of links
        """

        try:
            response = requests.get(nvd_rest_endpoint + vuln_id)
            if response.status_code != 200:
                return
            data = response.json()["result"]["CVE_Items"][0]
            self.published_timestamp = data["publishedDate"]
            self.last_modified_timestamp = data["lastModifiedDate"]
            self.description = data["cve"]["description"]["description_data"][0][
                "value"
            ]
            self.references = [
                r["url"] for r in data["cve"]["references"]["reference_data"]
            ]

        except:
            print("Could not retrieve vulnerability data from NVD for " + vuln_id)

    # """
    # Information to provide when initializing an advisory record
    # Input:
    #     vulnerability_id (str): the vulnerability ID, typically a CVE
    #     published_timestamp (str/int): the timestamp at which the vulnerability was
    #                                    published, or patched if that is known
    #     repo_url (str): the URL of the affected (GitHub) repository URL
    #     nvd_references (list): references to which the NVD refers (1st level references)
    #     references_content (str): the content that was extracted from these references,
    #                               and will be used to compare lexical similarity with
    #     advisory_references (list): the references that were extracted
    #                                 from the NVD references (2nd level references)
    #     vulnerability_description (str): the vulnerability description
    #     connection (sqlite3.connection): the connection with the (commits) database
    #     Optional:
    #         preprocessed_vulnerability_description (str): if there is already
    #                                       a preprocess vulnerability description
    #         relevant_tags (list): a list of tags that are regarded as relevant tags
    #                                (affected versions of the software)
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
    regex = r"([A-Z]+[a-z\b]+)"
    result = list(set(re.findall(regex, text)))
    return [p for p in result if len(p) > 2]


def extract_path_tokens(text: str) -> "list[str]":
    """
    Used to look for paths in the text (i.e. vulnerability description)

    Input:
        text (str)

    Returns:
        list: a list of paths that are found
    """
    return [
        re.split(r"\.|,|/", token.rstrip(r".,;:?!\"'"))
        for token in text.split(" ")
        if ("/" in token.rstrip(r".,;:?!\"'") and not token.startswith("</"))
        or (
            "." in token.rstrip(r".,;:?!\"'")
            and token.rstrip(r".,;:?!\"'").split(".")[-1] in RELEVANT_EXTENSIONS
        )
    ]


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
