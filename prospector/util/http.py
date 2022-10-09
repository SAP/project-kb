import re
from typing import List, Union
import requests
import requests_cache
from bs4 import BeautifulSoup

import log.util

_logger = log.util.init_local_logger()


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
        _logger.debug(f"cannot retrieve url content: {url}", exc_info=True)
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
        _logger.info("Contacting server " + server_url)

    try:
        response = requests.get(server_url)
        if response.status_code != 200:
            _logger.error(
                f"Server replied with an unexpected status: {response.status_code}"
            )
            return False
        else:
            _logger.info("Server ok!")
            return True
    except Exception:
        _logger.error("Server did not reply", exc_info=True)
        return False


def extract_from_webpage(url: str, attr_name: str, attr_value: List[str]) -> str:

    content = fetch_url(url, False)
    if not content:
        return ""

    return " ".join(
        [
            re.sub(r"\s+", " ", block.get_text())
            for block in content.find_all(attrs={attr_name: attr_value})
        ]
    ).strip()
