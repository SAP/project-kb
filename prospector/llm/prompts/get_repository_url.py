from langchain.prompts import FewShotPromptTemplate, PromptTemplate

# Get Repository URL, few-shot prompting examples
examples_data = [
    {
        "cve_description": "Apache Olingo versions 4.0.0 to 4.7.0 provide the AsyncRequestWrapperImpl class which reads a URL from the Location header, and then sends a GET or DELETE request to this URL. It may allow to implement a SSRF attack. If an attacker tricks a client to connect to a malicious server, the server can make the client call any URL including internal resources which are not directly accessible by the attacker.",
        "cve_references": "https://www.zerodayinitiative.com/advisories/ZDI-24-196/",
        "result": "https://github.com/apache/olingo-odata4",
    },
    {
        "cve_description": "Open-source project Online Shopping System Advanced is vulnerable to Reflected Cross-Site Scripting (XSS). An attacker might trick somebody into using a crafted URL, which will cause a script to be run in user's browser.",
        "cve_references": "https://cert.pl/en/posts/2024/05/CVE-2024-3579, https://cert.pl/posts/2024/05/CVE-2024-3579",
        "result": "https://github.com/PuneethReddyHC/online-shopping-system-advanced",
    },
    {
        "cve_description": "The Hoppscotch Browser Extension is a browser extension for Hoppscotch, a community-driven end-to-end open-source API development ecosystem. Due to an oversight during a change made to the extension in the commit d4e8e4830326f46ba17acd1307977ecd32a85b58, a critical check for the origin list was missed and allowed for messages to be sent to the extension which the extension gladly processed and responded back with the results of, while this wasn't supposed to happen and be blocked by the origin not being present in the origin list.\n\nThis vulnerability exposes Hoppscotch Extension users to sites which call into Hoppscotch Extension APIs internally. This fundamentally allows any site running on the browser with the extension installed to bypass CORS restrictions if the user is running extensions with the given version. This security hole was patched in the commit 7e364b928ab722dc682d0fcad713a96cc38477d6 which was released along with the extension version `0.35`. As a workaround, Chrome users can use the Extensions Settings to disable the extension access to only the origins that you want. Firefox doesn't have an alternative to upgrading to a fixed version.",
        "cve_references": "https://github.com/hoppscotch/hoppscotch-extension/commit/7e364b928ab722dc682d0fcad713a96cc38477d6, https://github.com/hoppscotch/hoppscotch-extension/commit/d4e8e4830326f46ba17acd1307977ecd32a85b58, https://github.com/hoppscotch/hoppscotch-extension/security/advisories/GHSA-jjh5-pvqx-gg5v, https://server.yadhu.in/poc/hoppscotch-poc.html",
        "result": "https://github.com/hoppscotch/hoppscotch-extension",
    },
]

# Formatter for the few-shot examples without CVE numbers
examples_formatted = PromptTemplate(
    input_variables=["cve_references", "result"],
    template="""<description> {cve_description} </description>
<references> {cve_references}</references>

<output> {result} </output>""",
)

prompt_best_guess = FewShotPromptTemplate(
    prefix="""You will be provided with the ID, description and references of a vulnerability advisory (CVE). Return nothing but the URL of the repository the given CVE is concerned with.'.

Here are a few examples delimited with XML tags:""",
    examples=examples_data,
    example_prompt=examples_formatted,
    suffix="""Here is the CVE information:
<description> {description} </description>
<references> {references} </references>

If you cannot find the URL, return your best guess of what the repository URL could be. Use any hints (eg. the mention of GitHub or GitLab) in the CVE description and references. Do not return the delimiters. Do not return delimiters. Return nothing but the URL.
""",
    input_variables=["description", "references"],
    metadata={"name": "prompt_best_guess"},
)
