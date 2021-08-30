from processing.natural_language_processing import extract_non_nl_terms


def test_extract_non_nl_terms():
    description = (
        "org.apache.http.conn.ssl.AbstractVerifier in Apache HttpComponents HttpClient "
        "before 4.3.5 and HttpAsyncClient before 4.0.2 does not properly verify that the "
        "server hostname matches a domain name in the subject's Common Name (CN) or "
        "subjectAltName field of the X.509 certificate, which allows man-in-the-middle "
        'attackers to spoof SSL servers via a "CN=" string in a field in the distinguished '
        'name (DN) of a certificate, as demonstrated by the "foo,CN=www.apache.org" string in '
        "the O field."
    )

    terms = tuple(extract_non_nl_terms(description))

    assert terms == (
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
