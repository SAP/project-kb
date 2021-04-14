from pprint import pprint

from .prospector_client import prospector


def test_prospector_client():
    results = prospector("CVE-2014-0050", "https://github.com/apache/struts")
    pprint(results)
