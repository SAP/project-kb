from acacia import git, utils
import os,sys
import plac
from pprint import pprint
from datetime import datetime

GIT_CACHE='/tmp/git-cache-3'

def extract_timing_data(commit_id, repo_url, verbose=False, git_cache=GIT_CACHE):

    if not os.path.exists(git_cache):
        print('Folder ' + git_cache + ' must exist!')
        return None

    # ensure the repository is available locally
    git.clone_repo(repo_url, output_folder=GIT_CACHE, skip_existing=True)

    cwd = os.path.join(git_cache, git.folder_name_from_url(repo_url))

    # get tag info
    tag = utils.execute('git tag --sort=taggerdate --contains ' + commit_id,  cwd=cwd)[0]
    if tag != '':
        tag_date = utils.execute('git show -s --format="%at" ' + tag + '^{commit}',  cwd=cwd)[0][1:-1]
    else:
        tag_date='0'

    try:
        commit_date =  utils.execute('git show -s --format="%ct" ' + commit_id,  cwd=cwd)[0][1:-1]
        time_delta = int(tag_date) - int(commit_date)
    except:
        commit_date = '0'
        time_delta = 0
        # print("exception:", commit_id, repo_url, commit_date, tag_date)

    if verbose:
        print('repository:                 ' + repo_url)
        print('commit:                     ' + commit_id)
        print('commit_date:                ' + commit_date)
        print('                            ' + datetime.utcfromtimestamp(int(commit_date)).strftime('%Y-%m-%d %H:%M:%S'))
        print('tag:                        ' + tag)
        print('tag_date:                   ' + tag_date)
        print('                            ' + datetime.utcfromtimestamp(int(tag_date)).strftime('%Y-%m-%d %H:%M:%S'))
        print('Commit-to-release interval: {0:.2f} days'.format( time_delta/(3600 * 24) ))

    result = (tag, tag_date, commit_date, time_delta )
    print(result)
    return ( result )

# (help, kind, abbrev, type, choices, metavar)
@plac.annotations(
    repo_url=("Repository", "positional", None, str, None, 'REPOSITORY'),
    commit_id=("Commit", "positional", None, str, None, 'COMMIT'),
    verbose=("Verbose", "flag", 'v', bool),
    git_cache= ("Git repository dir", "option", 'g', str, None, 'REPO_DIR')
    )
def main(repo_url, commit_id, verbose=False, git_cache=GIT_CACHE):
    return extract_timing_data(commit_id, repo_url, verbose, git_cache)

if __name__ == '__main__':
    import plac; plac.call(main)
