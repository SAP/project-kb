from pprint import pprint

from .prospector_client import prospector


def test_prospector_client():
    results = prospector("CVE-xxxx-yyyy", "https://github.com/apache/struts")
    pprint(results)
