import requests_cache
from bs4 import BeautifulSoup

import log.util

_logger = log.util.init_local_logger()


def fetch_url(url: str, extract_text=True) -> str:
    """fetch_url

    Args:
        url (str): target URL to fetch
        extract_text (bool, optional): Enables the extraction of human readable text from HTML pages. Defaults to True.

    Returns:
        str: text extracted from URL
    """

    try:
        session = requests_cache.CachedSession("requests-cache")
        content = session.get(url).text
    except Exception:
        _logger.debug(f"can not retrieve url content: {url}", exc_info=True)
        return ""

    if extract_text:
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text()

    return content
