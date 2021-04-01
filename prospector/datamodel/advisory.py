import re

# import requests

from dataclasses import dataclass, field
from . import BaseModel


@dataclass
class AdvisoryRecord:
    """
    The advisory record captures all relevant information on the vulnerability advisory
    """

    vulnerability_id: str
    repository_url: str
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
