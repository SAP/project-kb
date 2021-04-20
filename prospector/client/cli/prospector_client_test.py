from pprint import pprint

from .prospector_client import prospector
from .main import main


# def test_prospector_client():
#     results = prospector(
#         "CVE-2014-0050",
#         "https://github.com/apache/struts",
#         publication_date="2016-12-12T12:18Z",
#         debug=True,
#     )
#     pprint(results)


def test_main():
    args = [
        "PROGRAM_NAME",
        "CVE-2019-11278",
        "--repository",
        "https://github.com/cloudfoundry/uaa",
        "--tag-interval=v74.0.0:v74.1.0",
    ]
    main(args)


def test_main_ping_server():
    args = ["PROGRAM_NAME", "--verbose", "--ping"]
    main(args)
