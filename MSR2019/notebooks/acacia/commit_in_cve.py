# from acacia import git, utils
import os,sys
import plac
from pprint import pprint
from bs4 import BeautifulSoup
from bs4.element import Comment

import requests
import requests_cache
requests_cache.install_cache('requests_cache', expire_after=7 * 24*60*60)

NO_COMMIT_FOUND  = 0    # 'No reference to any commits was found')
CVE_MISSING = 1         # 'CVE not found in NVD')
CVE_NOT_PUBLIC = 2      # 'CVE id exists, but no description is available in the NVD')
CVE_HAS_GITHUB_LINK = 4 # 'A GIT link is present in the CVE description')
CVE_HAS_SVN_LINK = 8    # 'An SVN link is present in the CVE description')

def is_visible_text(e):
    if isinstance(e, Comment):
        return False
    if e.parent.name in ['title','script', 'head', 'style',  'meta', '[document]']:
        return False
    return True

def html_to_txt(body):
    bs = BeautifulSoup(body, 'html.parser')
    elements = bs.findAll(text=True)
    visible_txt = filter(is_visible_text, elements)
    return u" ".join(t.strip() for t in visible_txt)

def check_commit_in_cve(cve, verbose=False):
    result = NO_COMMIT_FOUND
    url = 'https://nvd.nist.gov/vuln/detail/' + cve

    r = requests.get(url)

    if r.status_code != 200 :
        result += CVE_MISSING
    else:
        page_txt = html_to_txt(r.text)

        if 'CVE ID Not Found' in page_txt:
            result += CVE_NOT_PUBLIC
        else:
            if 'git' in page_txt:
                result += CVE_HAS_GITHUB_LINK
            if 'svn' in page_txt:
                result += CVE_HAS_SVN_LINK

    if verbose:
        print('CVE:     ' + str(cve))
        print('         ' + str(url))
        print('Result:  ' + str(result))
        # print('       ' + str(result[1]))

    return ( url, result )

# (help, kind, abbrev, type, choices, metavar)
@plac.annotations(
    cve = ("CVE to check", "positional", None, str, None, 'REPOSITORY'),
    verbose = ("Verbose", "flag", 'v', bool)
    )
def main(cve, verbose):
    url, result = check_commit_in_cve(cve, verbose)
    print("{}\t{}".format(result, url))

if __name__ == '__main__':
    import plac; plac.call(main)
