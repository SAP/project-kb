# -*- coding: utf-8 -*-
"""Main module."""

import subprocess
import multiprocessing
import logging
import os
import sys
import shutil
# import traceback
# import random
import re
import difflib
# import hashlib
# from pprint import pprint
#import pickledb

import utils
from exec import Exec
from commit import Commit
# from datetime import datetime

GIT_CACHE = ''
if 'GIT_CACHE' in os.environ:
    GIT_CACHE = os.environ['GIT_CACHE']

if not os.path.isdir(GIT_CACHE):
    raise ValueError('Environment variable GIT_CACHE is not set or it points to a directory that does not exist')

def do_clone(url, output_folder, proxy=None, shallow=False, skip_existing=False):
    git = Git(url, cache_path=output_folder, shallow=shallow)
    git.clone(shallow=shallow, proxy=proxy, skip_existing=skip_existing)
    return git

def clone_repo_multiple(url_list,
                        output_folder,
                        proxy='',
                        shallow=False,
                        skip_existing=False,
                        concurrent=multiprocessing.cpu_count()):
    '''
    This is the parallelized version of clone_repo (works with a list of repositories).
    '''
    print('Using {} parallel workers'.format(concurrent))
    with multiprocessing.Pool(concurrent) as pool:
        args = ((url, output_folder, proxy, shallow, skip_existing) for url in url_list)
        results = pool.starmap(do_clone, args)

    return results

class Git:
    def __init__(self, url, cache_path=None, verbose=False, shallow=False):
        self.repository_type = 'GIT'
        self._verbose = verbose
        self._url = url
        self._path = os.path.join(cache_path, self._url.rstrip('/').split('/')[-1])
        self._fingerprints = dict()
        self._exec_timeout = None
        self._shallow_clone = shallow
        self.set_exec()
        self._storage = None

    def set_exec(self, exec_obj=None):
        if not exec_obj:
            self._exec = Exec(workdir=self._path)
        else:
            self._exec = exec_obj

    def get_url(self):
        return self._url

    def get_default_branch(self):
        '''
        Identifies the default branch of the remote repository for the local git
        repo
        '''
        logging.info('Identifiying remote branch for ' + self._path)

        try:
            cmd = 'git ls-remote -q'
            # self._exec._encoding = 'utf-8'
            l_raw_output = self._exec.run(cmd)

            logging.info('Identifiying sha1 of default remote ref among {} entries.'
                         .format(len(l_raw_output)))

            for raw_line in l_raw_output:
                if not raw_line:
                    continue
                (sha1, ref_name) = raw_line.split('\t')

                if ref_name == 'HEAD':
                    head_sha1 = sha1
                    logging.info('Remote head: ' + sha1)
                    break

        except subprocess.CalledProcessError as ex:
            logging.error('Exception happened while obtaining default remote branch for repository in ' + self._path)
            logging.error(str(ex))
            return None

        # ...then search the corresponding treeish among the local references
        try:
            cmd = 'git show-ref'
            # self._exec._encoding = 'utf-8'
            l_raw_output = self._exec.run(cmd)

            logging.info('Processing {} references'.format(len(l_raw_output)))

            for raw_line in l_raw_output:
                (sha1, ref_name) = raw_line.split()
                if sha1 == head_sha1:
                    return ref_name
            return None

        except Exception as ex:
            logging.error('Exception happened while obtaining default remote branch for repository in ' + self._path)
            logging.error(str(ex))
            return None

    def clone(self, input_file=None, proxy=None, shallow=None, skip_existing=False):
        '''
        Clones the specified repository checking out the default branch in a subdir of output_folder.
        Shallow=true speeds up considerably the operation, but gets no history.
        '''
        if shallow:
            self._shallow_clone = shallow

        if not self._url and input_file is None:
            print('url and input-file parameters cannot be both left unspecified')
            sys.exit(-1)

        # TODO rearrange order of checks
        if os.path.isdir(os.path.join(self._path, '.git')):
            if skip_existing:
                if self._verbose:
                    print('Skipping fetch of {} in {}'.format(self._url, self._path))
            else:
                if self._verbose:
                    print('\nFound repo {} in {}.\nFetching....'.format(self._url, self._path))

                self._exec.run(['git', 'fetch', '--progress', '--all', '--tags'])
                # , cwd=self._path, timeout=self._exec_timeout)
            return

        if os.path.exists(self._path):
            if self._verbose:
                print('Folder {} exists but it contains no git repository.'.format(self._path))
            return

        os.makedirs(self._path)

        if self._verbose:
            print('Cloning %s (shallow=%s)' % (self._url, self._shallow_clone))

        if not self._exec.run(['git', 'init'], ignore_output=True):
            print('Failed to initialize repository in %s' % self._path)

        try:
            self._exec.run(['git', 'remote', 'add', 'origin', self._url], ignore_output=True)
            #  , cwd=self._path)
        except Exception as ex:
            print('Could not update remote in %s (%s)' % (self._path, str(ex)))
            shutil.rmtree(self._path)
            raise ex

        if proxy:
            try:
                self._exec.run(['git', 'config', 'http.proxy', proxy]) #, cwd=self._path)
                self._exec.run(['git', 'config', 'https.proxy', proxy]) #, cwd=self._path)
            except Exception as ex:
                print('Error setting proxy for project %s in %s' % (self._url, self._path))
                print(str(ex))
                raise ex

        try:
            if self._shallow_clone:
                self._exec.run(['git', 'fetch', '--depth', '1']) #, cwd=self._path)
                # sh.git.fetch('--depth', '1', 'origin', _cwd=self._path)
            else:
                # sh.git.fetch('--all', '--tags', _cwd=self._path)
                self._exec.run(['git', 'fetch', '--progress', '--all', '--tags']) #, cwd=self._path)
                # self._exec.run_l(['git', 'fetch', '--tags'], cwd=self._path)
        except Exception as ex:
            print('Could not fetch %s (shallow=%s) in %s' % (self._url, str(self._shallow_clone), self._path))
            shutil.rmtree(self._path)
            raise ex

    def get_commits(self, ancestors_of=None, exclude_ancestors_of=None, since=None, until=None, filter_files='', find_in_code='', find_in_msg=''):
        if ancestors_of is None:
            cmd = ["git", "rev-list", "--all"]
        else:
            cmd = ["git", "rev-list"]

        if since:
            cmd.append("--since=" + since)

        if until:
            cmd.append("--until=" + until)

        if ancestors_of:
            cmd.append(ancestors_of)

        if exclude_ancestors_of:
            cmd.append('^'+exclude_ancestors_of)

        if filter_files:
            cmd.append(filter_files)

        if find_in_code:
            cmd.append("-S\"%s\"" % find_in_code)

        if find_in_msg:
            cmd.append("--grep=\"%s\"" % find_in_msg)

        try:
            print(" ".join(cmd))
            out = self._exec.run(cmd)
        except Exception as ex:
            sys.stderr.write("Git command failed, cannot get commits \n%s" % str(ex))
            out = []

        out = [l.strip() for l in out]
        return out

    def get_commit(self, key, by='id'):
        if by == 'id':
            return Commit(self, key, self._verbose)
        if by == 'fingerprint':
            # TODO implement computing fingerprints
            c_id = self._fingerprints[key]
            return Commit(self, c_id, self._verbose)

        return None

    def get_random_commits(self, count):
        '''
        Return a list of n random commits from repo, which is assumed to be available
        as a standard-named subdirectory of base_dir
        '''
        return utils.reservoir_sampling(self.get_commits(), count)

    def get_tag_for_version(self, version):
        '''
        get closest match from tags, given the version id
        '''
        # return Levenshtein.ratio('hello world', 'hello')
        version = re.sub("[^0-9]", "", version)

        tags = self.get_tags()
        best_match = ('', 0.0)
        for tag in tags:
            t_strip = re.sub("[^0-9]", "", tag)
            match_score = difflib.SequenceMatcher(None, t_strip, version).ratio()
            # print(t, match_score)
            if match_score > best_match[1]:
                best_match = (tag, match_score)

        return best_match

    # def pretty_print_tag_ref(self, ref):
    #     return ref.split('/')[-1]

    def get_tags(self):
        try:
            tags = self._exec.run('git tag')
        except subprocess.CalledProcessError as exc:
            print('Git command failed.' + str(exc.output))
            tags = []

        if not tags:
            tags = []

        return tags

    def get_commit_id_for_tag(self, tag):
        cmd = 'git rev-list -n1 ' + tag
        cmd = cmd.split()

        try:
            # @TODO: https://stackoverflow.com/questions/16198546/get-exit-code-and-stderr-from-subprocess-call
            commit_id = subprocess.check_output(cmd, cwd=self._path).decode()
        except subprocess.CalledProcessError as exc:
            print('Git command failed.' + str(exc.output))
            sys.exit(1)
        if not commit_id:
            return None
        return commit_id.strip()

    def get_previous_tag(self, tag):
        # https://git-scm.com/docs/git-describe
        commit_for_tag = self.get_commit_id_for_tag(tag)
        cmd = 'git describe --abbrev=0 --all --tags --always ' + commit_for_tag + '^'
        cmd = cmd.split()

        try:
            # @TODO: https://stackoverflow.com/questions/16198546/get-exit-code-and-stderr-from-subprocess-call
            tags = self._exec.run(cmd)
        except subprocess.CalledProcessError as exc:
            print('Git command failed.' + str(exc.output))
            return []

        if not tags:
            return []

        return tags