import pytest

from data_sources.nvd.versions_extraction import (
    extract_version_range,
    extract_version_ranges_cpe,
    extract_version_ranges_description,
    process_versions,
)

ADVISORY_TEXT_1 = "In Eclipse Jetty versions 9.4.21.v20190926, 9.4.22.v20191022, and 9.4.23.v20191118, the generation of default unhandled Error response content (in text/html and text/json Content-Type) does not escape Exception messages in stacktraces included in error output."
ADVISORY_TEXT_2 = "Apache Olingo versions 4.0.0 to 4.7.0 provide the AsyncRequestWrapperImpl class which reads a URL from the Location header, and then sends a GET or DELETE request to this URL. It may allow to implement a SSRF attack. If an attacker tricks a client to connect to a malicious server, the server can make the client call any URL including internal resources which are not directly accessible by the attacker."
ADVISORY_TEXT_3 = "Pivotal Spring Framework through 5.3.16 suffers from a potential remote code execution (RCE) issue if used for Java deserialization of untrusted data. Depending on how the library is implemented within a product, this issue may or not occur, and authentication may be required. NOTE: the vendor's position is that untrusted data is not an intended use case. The product's behavior will not be changed because some users rely on deserialization of trusted data."
ADVISORY_TEXT_4 = "Integer overflow in java/org/apache/tomcat/util/buf/Ascii.java in Apache Tomcat before 6.0.40, 7.x before 7.0.53, and 8.x before 8.0.4, when operated behind a reverse proxy, allows remote attackers to conduct HTTP request smuggling attacks via a crafted Content-Length HTTP header."
ADVISORY_TEXT_5 = "FasterXML jackson-databind through 2.8.10 and 2.9.x through 2.9.3 allows unauthenticated remote code execution because of an incomplete fix for the CVE-2017-7525 deserialization flaw. This is exploitable by sending maliciously crafted JSON input to the readValue method of the ObjectMapper, bypassing a blacklist that is ineffective if the Spring libraries are available in the classpath."
ADVISORY_TEXT_6 = "Allocation of Resources Without Limits or Throttling vulnerability in Apache Software Foundation Apache Struts.This issue affects Apache Struts: through 2.5.30, through 6.1.2.\n\nUpgrade to Struts 2.5.31 or 6.1.2.1 or greater."
JSON_DATA_1 = {
    "configurations": [
        {
            "nodes": [
                {
                    "cpeMatch": [
                        {"versionStartIncluding": "1.0", "versionEndIncluding": "2.0"},
                        {"versionStartExcluding": "2.0", "versionEndExcluding": "3.0"},
                        {"versionStartIncluding": "4.0", "versionEndIncluding": "5.0"},
                    ]
                },
            ]
        }
    ]
}

JSON_DATA_2 = {
    "configurations": [
        {
            "nodes": [
                {
                    "cpeMatch": [
                        {
                            "criteria": "cpe:2.3:a:fasterxml:jackson-databind:*:*:*:*:*:*:*:*",
                            "versionEndExcluding": "2.6.7.3",
                            "matchCriteriaId": "1DF0B092-75D2-4A01-9CDC-B3AB2F4CF2C3",
                        },
                        {
                            "criteria": "cpe:2.3:a:fasterxml:jackson-databind:*:*:*:*:*:*:*:*",
                            "versionStartIncluding": "2.7.0",
                            "versionEndExcluding": "2.7.9.2",
                            "matchCriteriaId": "5BBA4A48-37C7-4165-B422-652EFD99B05B",
                        },
                        {
                            "criteria": "cpe:2.3:a:fasterxml:jackson-databind:*:*:*:*:*:*:*:*",
                            "versionStartIncluding": "2.8.0",
                            "versionEndExcluding": "2.8.11",
                            "matchCriteriaId": "2D1029A9-A17E-43FE-BE78-DF2DEEBFBAAF",
                        },
                        {
                            "criteria": "cpe:2.3:a:fasterxml:jackson-databind:*:*:*:*:*:*:*:*",
                            "versionStartIncluding": "2.9.0",
                            "versionEndExcluding": "2.9.4",
                            "matchCriteriaId": "603345A2-FA66-4B4C-9143-AE710EF6626F",
                        },
                    ]
                }
            ]
        },
        {
            "nodes": [
                {
                    "cpeMatch": [
                        {
                            "criteria": "cpe:2.3:o:debian:debian_linux:8.0:*:*:*:*:*:*:*",
                            "matchCriteriaId": "C11E6FB0-C8C0-4527-9AA0-CB9B316F8F43",
                        },
                        {
                            "criteria": "cpe:2.3:o:debian:debian_linux:9.0:*:*:*:*:*:*:*",
                            "matchCriteriaId": "DEECE5FC-CACF-4496-A3E7-164736409252",
                        },
                    ]
                }
            ]
        },
    ]
}

JSON_DATA_3 = {
    "configurations": [
        {
            "nodes": [
                {
                    "cpeMatch": [
                        {
                            "criteria": "cpe:2.3:a:jenkins:pipeline_utility_steps:*:*:*:*:*:jenkins:*:*",
                            "versionEndIncluding": "2.15.2",
                            "matchCriteriaId": "C6754B3C-6C9D-4EE8-A27F-7EA327B90CB6",
                        }
                    ]
                }
            ]
        }
    ]
}

JSON_DATA_4 = {}


VERSION_RANGES = ["[1.0:2.0]", "(2.0:3.0)", "[2.1:None)", "[4.0:5.0]"]


def test_extract_version_ranges_description():
    version_range = extract_version_ranges_description(ADVISORY_TEXT_1)
    assert version_range == "9.4.23:None"

    version_range = extract_version_ranges_description(ADVISORY_TEXT_2)
    assert version_range == "4.7.0:None"

    version_range = extract_version_ranges_description(ADVISORY_TEXT_3)
    assert version_range == "5.3.16:None"

    version_range = extract_version_ranges_description(ADVISORY_TEXT_4)
    assert version_range == "None:8.0.4"

    version_range = extract_version_ranges_description(ADVISORY_TEXT_6)
    assert version_range == "6.1.2:None"


def test_extract_version_ranges_cpe():
    version_ranges = extract_version_ranges_cpe(JSON_DATA_1)
    assert version_ranges == ["[1.0:2.0]", "(2.0:3.0)", "[4.0:5.0]"]

    version_ranges = extract_version_ranges_cpe(JSON_DATA_2)
    assert version_ranges == [
        "(None:2.6.7.3)",
        "[2.7.0:2.7.9.2)",
        "[2.8.0:2.8.11)",
        "[2.9.0:2.9.4)",
    ]

    version_ranges = extract_version_ranges_cpe(JSON_DATA_3)
    assert version_ranges == ["(None:2.15.2]"]


def test_process_ranges():
    version_ranges = process_versions(VERSION_RANGES)
    assert version_ranges == "4.0:5.1"


def test_extract_version_ranges():
    version_range = extract_version_range(JSON_DATA_4, ADVISORY_TEXT_6)
    assert version_range == "6.1.2:None"
