from .nlp import (
    extract_affected_filenames,
    extract_ghissue_references,
    extract_jira_references,
    find_similar_words,
)


def test_extract_similar_words():
    commit_msg = "Is this an advisory message?"
    adv_text = "This is an advisory description message"
    similarities = find_similar_words(
        set(adv_text.casefold().split()), commit_msg, "simola"
    )
    assert similarities.pop() == "message"


ADVISORY_TEXT_1 = """CXF supports (via JwtRequestCodeFilter) passing OAuth 2 parameters via a JWT token as opposed to query parameters (see: The OAuth 2.0 Authorization Framework: JWT Secured Authorization Request (JAR)). Instead of sending a JWT token as a "request" parameter, the spec also supports specifying a URI from which to retrieve a JWT token from via the "request_uri" parameter. CXF was not validating the "request_uri" parameter (apart from ensuring it uses "https) and was making a REST request to the parameter in the request to retrieve a token. This means that CXF was vulnerable to DDos attacks on the authorization server, as specified in section 10.4.1 of the spec. This issue affects Apache CXF versions prior to 3.4.3; Apache CXF versions prior to 3.3.10."""

ADVISORY_TEXT_2 = """org/mitre/oauth2/web/OAuthConfirmationController.java in the OpenID Connect server implementation for MITREid Connect through 1.3.3 contains a Mass Assignment (aka Autobinding) vulnerability. This arises due to unsafe usage of the @ModelAttribute annotation during the OAuth authorization flow, in which HTTP request parameters affect an authorizationRequest."""

ADVISORY_TEXT_3 = """In Apache Commons IO before 2.7, When invoking the method FileNameUtils.normalize with an improper input string, like "//../foo", or "\\..\foo", the result would be the same value, thus possibly providing access to files in the parent directory, but not further above (thus "limited" path traversal), if the calling code would use the result to construct a path value."""

ADVISORY_TEXT_4 = """"MultipartStream.java in Apache Commons FileUpload before 1.3.1, as used in Apache Tomcat, JBoss Web, and other products, allows remote attackers to cause a denial of service (infinite loop and CPU consumption) via a crafted Content-Type header that bypasses a loop's intended exit conditions."""

ADVISORY_TEXT_5 = """A vulnerability in the JsonMapObjectReaderWriter of Apache CXF allows an attacker to submit malformed JSON to a web service, which results in the thread getting stuck in an infinite loop, consuming CPU indefinitely. This issue affects Apache CXF versions prior to 3.4.4; Apache CXF versions prior to 3.3.11."""


def test_extract_affected_filenames():
    result1 = extract_affected_filenames(ADVISORY_TEXT_1)
    result2 = extract_affected_filenames(ADVISORY_TEXT_2)
    result3 = extract_affected_filenames(ADVISORY_TEXT_3)
    result4 = extract_affected_filenames(ADVISORY_TEXT_4)
    result5 = extract_affected_filenames(ADVISORY_TEXT_5)
    assert result1 == set(["JwtRequestCodeFilter", "request_uri"])
    assert result2 == set(
        [
            "OAuthConfirmationController.java",
            "@ModelAttribute",
            "authorizationRequest",
            "OpenID",
        ]
    )
    assert result3 == set(["FileNameUtils"])

    assert result4 == set(["MultipartStream.java", "FileUpload"])  # Content-Type
    assert result5 == set(["JsonMapObjectReaderWriter"])


def test_adv_record_path_extraction_has_real_paths():
    # result = extract_affected_files_paths(ADVISORY_TEXT_2)
    print("")
    # assert result == ["FileNameUtils", "//../foo", "\\..\\foo"]


def test_adv_record_path_extraction_strict_extensions():
    """
    If strict_extensions is True, it will always extract tokens with (back) slashes,
    but it will only collect single file names if they have the correct extension.
    """
    # result = extract_affected_files_paths(
    #     ADVISORY_TEXT_2
    #     + " Developer.gery put something here to check if foo.java and bar.cpp will be found.",
    #     strict_extensions=True,
    # )
    print("result")
    # assert result == ["FileNameUtils", "//../foo", "\\..\\foo", "foo", "bar"]


def test_extract_jira_references():
    x = extract_jira_references("apache/ambari", "AMBARI-25329")
    print(x)
    pass


def test_extract_gh_issues():
    d = extract_ghissue_references("https://github.com/slackhq/nebula", "#310")
    print(d)
    pass
