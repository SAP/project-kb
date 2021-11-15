from .nlp import (
    extract_cve_references,
    extract_jira_references,
    extract_path_tokens,
    extract_special_terms,
)


def test_extract_special_terms():
    description = (
        "org.apache.http.conn.ssl.AbstractVerifier in Apache HttpComponents HttpClient "
        "before 4.3.5 and HttpAsyncClient before 4.0.2 does not properly verify that the "
        "server hostname matches a domain name in the subject's Common Name (CN) or "
        "subjectAltName field of the X.509 certificate, which allows man-in-the-middle "
        'attackers to spoof SSL servers via a "CN=" string in a field in the distinguished '
        'name (DN) of a certificate, as demonstrated by the "foo,CN=www.apache.org" string in '
        "the O field."
    )

    terms = extract_special_terms(description)

    # TODO replace when NLP implementation is done
    # see, https://github.com/SAP/project-kb/issues/256#issuecomment-927639866
    assert terms == () or terms == (
        "org.apache.http.conn.ssl.AbstractVerifier",
        "HttpComponents",
        "HttpClient",
        "4.3.5",
        "HttpAsyncClient",
        "4.0.2",
        "subject's",
        "(CN)",
        "subjectAltName",
        "X.509",
        "man-in-the-middle",
        "SSL",
        '"CN="',
        "(DN)",
        '"foo,CN=www.apache.org"',
    )


def test_adv_record_path_extraction_no_real_paths():
    result = extract_path_tokens(ADVISORY_TEXT)

    assert result == ["15.26.1", '\\"Radio', "protection,\\"]


ADVISORY_TEXT = """Unspecified vulnerability in Uconnect before 15.26.1, as used
    in certain Fiat Chrysler Automobiles (FCA) from 2013 to 2015 models, allows
    remote attackers in the same cellular network to control vehicle movement,
    cause human harm or physical damage, or modify dashboard settings via
    vectors related to modification of entertainment-system firmware and access
    of the CAN bus due to insufficient \\"Radio security protection,\\" as
    demonstrated on a 2014 Jeep Cherokee Limited FWD."""

ADVISORY_TEXT_2 = """In Apache Commons IO before 2.7, When invoking the method FileNameUtils.normalize
with an improper input string, like "//../foo", or "\\..\\foo", the result would be
the same value, thus possibly providing access to files in the parent directory,
but not further above (thus "limited" path traversal), if the calling code would
use the result to construct a path value."""


def test_adv_record_path_extraction_has_real_paths():
    result = extract_path_tokens(ADVISORY_TEXT_2)

    assert result == ["2.7", "FileNameUtils.normalize", "//../foo", "\\..\\foo"]


def test_adv_record_path_extraction_strict_extensions():
    """
    If strict_extensions is True, it will always extract tokens with (back) slashes,
    but it will only collect single file names if they have the correct extension.
    """
    result = extract_path_tokens(
        ADVISORY_TEXT_2
        + " Developer.gery put something here to check if foo.java and bar.cpp will be found.",
        strict_extensions=True,
    )

    assert result == ["//../foo", "\\..\\foo", "foo.java", "bar.cpp"]


def test_extract_cve_identifiers():
    result = extract_cve_references(
        "bla bla bla CVE-1234-1234567 and CVE-1234-1234, fsafasf"
    )
    assert result == {"CVE-1234-1234": "", "CVE-1234-1234567": ""}


def test_extract_jira_references():
    commit_msg = "CXF-8535 - Checkstyle fix (cherry picked from commit bbcd8f2eb059848380fbe5af638fe94e3a9a5e1d)"

    assert extract_jira_references(commit_msg) == {"CXF-8535": None}


def test_extract_jira_references_lowercase():
    commit_msg = "cxf-8535 - Checkstyle fix (cherry picked from commit bbcd8f2eb059848380fbe5af638fe94e3a9a5e1d)"

    assert extract_jira_references(commit_msg) == {}
