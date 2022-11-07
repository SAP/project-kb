import re
from typing import List, Union

import requests
import requests_cache
from bs4 import BeautifulSoup

from log.logger import logger


def fetch_url(url: str, extract_text=True) -> Union[str, BeautifulSoup]:
    """fetch_url

    Args:
        url (str): target URL to fetch
        extract_text (bool, optional): Enables the extraction of human readable text from HTML pages. Defaults to True.

    Returns:
        str: text extracted from URL
    """
    try:
        session = requests_cache.CachedSession("requests-cache")
        content = session.get(url).content
    except Exception:
        logger.debug(f"cannot retrieve url content: {url}", exc_info=True)
        return ""

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


def extract_from_webpage(url: str, attr_name: str, attr_value: List[str]) -> str:

    content = fetch_url(url, False)
    if not content:
        return ""

    return " ".join(
        [
            block.get_text()  # re.sub(r"\s+", " ", block.get_text())
            for block in content.find_all(attrs={attr_name: attr_value})
        ]
    ).strip()


def get_from_xml(id: str):
    try:
        params = {"field": {"description", "summary"}}

        response = requests.get(
            f"https://issues.apache.org/jira/si/jira.issueviews:issue-xml/{id}/{id}.xml",
            params=params,
        )
        xml_data = BeautifulSoup(response.text, features="html.parser")
        item = xml_data.find("item")
        description = re.sub(r"<\/?p>", "", item.find("description").text)
        summary = item.find("summary").text
    except Exception:
        logger.debug(f"cannot retrieve jira issue content: {id}", exc_info=True)
        return ""
    return f"{summary} {description}"
