import subprocess
import multiprocessing
import logging
import os, sys
import sh
import re
from . import utils
from tqdm import tqdm
import random


# stopwords = set(['apache',
#              'index',
#              'trunk',
#              'branches',
#              'java',
#              'the',
#              'src',
#              'main',
#              'revision',
#              'private',
#              'public',
#              'int',
#              'class',
#              'static',
#              'string',
#              'org',
#              'foo',
#              'due',
#              'commons',
#              'junit',
#              'english',
#              'collections']
#              )

# Donald Knuth's "reservoir sampling"
# http://data-analytics-tools.blogspot.de/2009/09/reservoir-sampling-algorithm-in-perl.html
def reservoir_sampling(input_list, N):
    sample = []
    for i, line in enumerate(input_list):
        if i < N:
            sample.append(line)
        elif i >= N and random.random() < N / float(i + 1):
            replace = random.randint(0, len(sample) - 1)
            sample[replace] = line
    return sample

def folder_name_from_url(url):
    if url[-1] == '/':
        url = url[:-1]

    return  url.split('/')[-1]

# def identifyDefaultRemoteBranch(dir):
#     '''
#     Identifies the default branch of the remote repository for the local git
#     repo (that is in 'dir')
#     '''

#     logging.info('Identifiying remote branch for ' + dir)
#     references = {}
#     """
#     first get sha1 of default remote ref
#     """
#     cmd = 'git ls-remote -q'
#     # pdb.set_trace()
#     try:
#         # os.chdir(dir_name)
#         p = subprocess.Popen(cmd.split(), cwd=dir, stdout=subprocess.PIPE)
#         out, err = p.communicate()
#         if err:
#             logging.error(str(err))
#             return None
#         #
#         raw_output_list = out.decode("utf-8").split('\n')

#         logging.info('Identifiying sha1 of default remote ref among {} entries.'.format(len(raw_output_list)))
#         # logging.info('Identifiying sha1 of default remote ref among {} entries.'.format(len(raw_output_list)))

#         for r in raw_output_list:
#             if len(r) == 0:
#                 continue
#             (sha1, ref_name) = r.split('\t')
#             # pdb.set_trace()

#             if ref_name == 'HEAD':
#                 # pdb.set_trace()
#                 head_sha1 = sha1
#                 logging.info('Remote head: ' + sha1)
#                 break

#     except Exception as e:
#         logging.error('Exception happened while obtaining default remote branch for repository in ' + dir)
#         logging.error(str(e))
#         return None

#     """
#     ...then search the corresponding treeish among the local references
#     """
#     cmd = 'git show-ref'
#     try:
#         # os.chdir(dir_name)
#         p2 = subprocess.Popen(cmd.split(), cwd=dir, stdout=subprocess.PIPE)
#         out, err = p2.communicate()
#         if err:
#             logging.error(str(err))
#             return None
#         #
#         raw_output_list = out.decode('utf-8').split('\n')

#         logging.info('Processing {} references'.format(len(raw_output_list)))

#         for r in raw_output_list:
#             (sha1, ref_name) = r.split()
#             if sha1 == head_sha1:
#                 return ref_name
#         return None

#     except Exception as e:
#         logging.error('Exception happened while obtaining default remote branch for repository in ' + dir)
#         logging.error(str(e))
#         return None

def clone_repo_multiple(url_list, output_folder, proxy='', shallow=False, skip_existing=False, concurrent=4):
    '''
    This is the parallelized version of clone_repo (works with a list of repositories).
    '''

    with multiprocessing.Pool(concurrent) as pool:
        args = ((url, output_folder, None, proxy, shallow, skip_existing) for url in url_list)
        results = pool.starmap(clone_repo, args)

    # return results

    # for repo in tqdm(url_list):
    #     clone_repo(repo,
    #                output_folder=output_folder,
    #                proxy=proxy,
    #                shallow=shallow,
    #                skip_existing=skip_existing)

def clone_repo(url, output_folder, input_file=None, proxy=None, shallow=False, skip_existing=False):
    '''
    Clones the specified repository checking out the default branch in a subdir of output_folder.
    Shallow=true speeds up considerably the operation, but no history.
    '''
    if len(url) == 0 and len(input_file) == 0:
        print('url and input-file parameters cannot be both left unspecified')
        sys.exit(-1)

    repo_name = folder_name_from_url(url)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    repo_folder = os.path.join(output_folder, repo_name)

    if os.path.isdir(repo_folder):
        if skip_existing:
            # print('Skipping {} in {}'.format(url,repo_folder))
            pass
        else:
            # print('Fetching for existing repo {} in {}'.format(url,repo_folder))
            # sh.git.fetch('origin', _cwd=repo_folder)
            sh.git.fetch('--all', '--tags', _cwd=repo_folder)

        return
    else:
        os.makedirs('%s' % repo_folder)

    print('Processing %s' % url)

    try:
        sh.git.init( _cwd=repo_folder)
    except:
        print('Could not initialize repository in %s (already initialized?)' % repo_folder)

    try:
        sh.git.remote('add',  'origin', '%s' % url , _cwd=repo_folder)
    except:
        print('Could not update remote in %s' % repo_folder)

    if proxy:
        try:
            sh.git.config("http.proxy","{}".format(proxy), _cwd=repo_folder)
            sh.git.config("https.proxy", "{}".format(proxy), _cwd=repo_folder)
        except sh.ErrorReturnCode_128:
            print('Error setting proxy for project %s in %s' % (repo_name, repo_folder) )

    try:
        if shallow:
            sh.git.fetch('--depth', '1', 'origin', _cwd=repo_folder)
        else:
            # sh.git.fetch('--all', _cwd=repo_folder)
            sh.git.fetch('--all', '--tags', _cwd=repo_folder)
    except:
        print('Could not fetch %s (shallow=%s) in %s' % (url, str(shallow), repo_folder))
        return

    # print('Fetch of %s (shallow=%s) in %s completed' % (url, str(shallow), repo_folder))

    # default_remote_branch = identifyDefaultRemoteBranch(repo_folder) or 'origin/master'
    #
    # sh.git.checkout(default_remote_branch, _cwd=repo_folder)

def get_random_commits(n, repo, base_dir):
    '''
    Return a list of n random commits from repo, which is assumed to be available
    as a standard-named subdirectory of base_dir
    '''
    git_opts = ["--all", "--format=%H"]
    repo_name = folder_name_from_url(repo)
    cwd = os.path.join(base_dir,repo_name)
    try:
        all_commits = sh.git("log","--all", "--format=%H", _cwd=cwd)
    except subprocess.CalledProcessError:
        print("Git command failed, cannot get random commits")
        return []

    all_commits = [ n.strip() for n in all_commits ]
    # Donald Knuth's "reservoir sampling"
    # http://data-analytics-tools.blogspot.de/2009/09/reservoir-sampling-algorithm-in-perl.html
    return reservoir_sampling(all_commits, n)


def extract_commit_msg(commit_id, repo, base_dir):
    '''
    Extracts log message of commit_id assuming that the repo has been
    previously cloned in a subdirectory of dir (whose name is inferred from the repo url)
    '''

    # repo_name =  repo.replace('/',' ').split(' ')[-1]
    repo_name = folder_name_from_url(repo)

    cwd = os.path.join(base_dir,repo_name)
    try:
        out = sh.git.log("--format=%s", "-n1", commit_id, _cwd=cwd)
    except:
        print('Failed to obtain commit message for commit: %s in dir: %s' % (commit_id, cwd))
        return None

    return out.stdout

def extract_commit_diff(commit_id, repo, base_dir):
    '''
    Extracts patch for commit_id assuming that a valid repo has been
    previously cloned in dir
    '''
    repo_name = folder_name_from_url(repo)
    cwd = os.path.join(base_dir,repo_name)
    try:
        out = sh.git.diff( commit_id + "^.." + commit_id, _cwd=cwd, _tty_out=False)
        # out = unicode(out, errors='ignore')

    except:
        print('Failed to obtain patch for commit: %s in dir: %s' % (commit_id, cwd))
        return None

    return out.stdout
