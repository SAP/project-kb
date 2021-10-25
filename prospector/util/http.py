import requests_cache

import log.util

_logger = log.util.init_local_logger()


def fetch_url(url: str) -> str:

    try:
        session = requests_cache.CachedSession("requests-cache")
        content = session.get(url).text
    except Exception:
        _logger.debug(f"can not retrieve url content: {url}", exc_info=True)
        return ""

    return content
