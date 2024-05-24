import re
from typing import List, Union

import requests
import requests_cache
from bs4 import BeautifulSoup

from log.logger import logger


def fetch_url(url: str, params=None, extract_text=True) -> Union[str, BeautifulSoup]:
    """
    Fetches the content of a web page located at the specified URL and optionally extracts text from it.

    Parameters:
    - url (str): The URL of the web page to fetch.
    - params (dict, optional): Optional parameters to be sent with the request (default: None).
    - extract_text (bool, optional): Whether to extract text content from the HTML (default: True).

    Returns:
    - Union[str, BeautifulSoup]: If `extract_text` is True, returns the text content of the web page as a string.
      If `extract_text` is False, returns the parsed HTML content as a BeautifulSoup object.

    If an exception occurs during the HTTP request, an empty string ("") is returned.
    """
    try:
        session = requests_cache.CachedSession("requests-cache", expire_after=604800)
        if params is None:
            content = session.get(url).content
        else:
            content = session.get(url, params=params).content
    except Exception:
        logger.debug(f"cannot retrieve url content: {url}", exc_info=True)
        return None

    soup = BeautifulSoup(content, "html.parser")
    if extract_text:
        return soup.get_text()

    return soup


def ping_backend(server_url: str, verbose: bool = False) -> bool:
    """Tries to contact backend server

    Args:
        server_url (str): the URL of the server endpoint
        verbose (bool, optional): enable verbose output. Defaults to False.
    """

    if verbose:
        logger.info("Contacting server " + server_url)

    try:
        response = requests.get(server_url)
        if response.status_code != 200:
            logger.error(
                f"Server replied with an unexpected status: {response.status_code}"
            )
            return False
        else:
            logger.info("Server sok!")
            return True
    except requests.RequestException:
        logger.error("Server did not reply", exc_info=True)
        return False


def get_urls(url: str) -> List[str]:
    content = fetch_url(url, extract_text=False)
    if not content:
        return []

    return [link.get("href") for link in content.find_all("a", href=True)]


# TODO: properly scrape github issues
def extract_from_webpage(url: str, attr_name: str, attr_value: List[str]) -> str:

    content = fetch_url(url, None, False)
    if not content:
        return ""
    print(content.get_text())
    print(
        [result.group(0) for result in re.finditer(r"[A-Z]+-\d+", content.get_text())]
    )
    return [
        link.get("href")
        for link in content.find_all(
            "a",
            attrs={
                "href": re.compile(
                    r"^https://github.com|^https://issues.apache.org/jira"
                )
            },
        )
    ]
    # display the actual urls

    # return [
    #     block.get_text()  # re.sub(r"\s+", " ", block.get_text())
    #     for block in content.find_all(attrs={attr_name: attr_value})
    # ]


def get_from_xml(id: str):
    try:
        params = {"field": {"description", "summary", "comments"}}

        # response = requests.get(
        #     f"https://issues.apache.org/jira/si/jira.issueviews:issue-xml/{id}/{id}.xml",
        #     params=params,
        # )
        # xml_data = BeautifulSoup(response.text, features="html.parser")
        xml_data = fetch_url(
            f"https://issues.apache.org/jira/si/jira.issueviews:issue-xml/{id}/{id}.xml",
            params=params,
        )
        item = xml_data.find("item")
        if item is None:
            return ""
        relevant_data = [
            itm.text for itm in item.findAll(["description", "summary", "comments"])
        ]

        relevant_data = BeautifulSoup("\n".join(relevant_data), features="html.parser")

        return " ".join(relevant_data.stripped_strings)
    except Exception:
        return ""
