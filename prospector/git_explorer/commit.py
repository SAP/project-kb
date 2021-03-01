import subprocess
import multiprocessing
import logging
import os
import sys
import random
import re
# from tqdm import tqdm
import difflib
import hashlib
from pprint import pprint
#import pickledb

import utils
from exec import Exec
from datetime import datetime
import traceback


class Commit:
    def __init__(self, repository, commit_id, init_data=None, verbose=False):
        self._attributes = {}

        self._repository = repository
        self._id = commit_id
        self._exec = repository._exec

        self._verbose = verbose

        # the following attributes will be initialized lazily and memoized, unless init_data is not None
        if init_data:
            for k in init_data:
                self._attributes[k] = init_data[k]
        # else:
        #     self._msg = []
        #     self._full_id = None
        #     self._diff = []
        #     self._timestamp = None
        #     self._fingerprint = None
        #     self._hunks = []
        #     self._changed_files = None
        #     self._next_tag = None
        #     self._next_tag_timestamp = None
        #     self._timestamp = None
        #     self._time_to_tag = None

    def get_id(self):
        if 'full_id' not in self._attributes:
            try:
                cmd = ['git', 'log', '--format=%H', '-n1', self._id]
                self._attributes['full_id'] = self._exec.run(cmd)[0]
            except:
                print('Failed to obtain full commit id for: %s in dir: %s' % (self._id, self._exec._workdir))
        return (self._id, self._attributes['full_id'])

    def get_msg(self):
        if 'msg' not in self._attributes:
            self._attributes['msg'] = ''
            try:
                cmd = ['git', 'log', '--format=%B', '-n1', self._id]
                self._attributes['msg'] = ' '.join(self._exec.run(cmd))
            except:
                print('Failed to obtain commit message for commit: %s in dir: %s' % (self._id, self._exec._workdir))
        return self._attributes['msg']

    def get_diff(self, context_size=1, filter_files=''):
        if 'diff' not in self._attributes:
            self._attributes['diff'] = ''
            try:
                cmd = ['git', 'diff', '--unified=' + str(context_size), self._id + "^.." + self._id]
                if filter_files:
                    cmd.append(filter_files)
                self._attributes['diff'] = self._exec.run(cmd)
            except:
                print('Failed to obtain patch for commit: %s in dir: %s' % (self._id, self._exec._workdir))
        return self._attributes['diff']

    def get_timestamp(self, date_format=None):
        if 'timestamp' not in self._attributes:
            self._attributes['timestamp'] = None
            self._get_timing_data()
            # self._timestamp = self.timing_data()[2]
        if date_format:
            return datetime.utcfromtimestamp(int(self._attributes['timestamp'])).strftime(date_format)
        return self._attributes['timestamp']


    def get_changed_files(self):
        if 'changed_files' not in self._attributes:
            cmd = [ 'git', 'diff', '--name-only', self._id +'^..'+ self._id ]
            out = self._exec.run(cmd)
            self._attributes['changed_files'] = out
        return self._attributes['changed_files']

    def get_changed_paths(self, other_commit=None, match=None):
        # TODO refactor, this overlaps with changed_files

        if other_commit is None:
            other_commit_id = self._id + '^'
        else:
            other_commit_id = other_commit._id

        cmd = [ 'git', 'log', '--name-only',  '--format=%n', '--full-index', other_commit_id +'..'+ self._id ]
        try:
            out = self._exec.run(cmd)
        except Exception as e:
            out = str()
            sys.stderr.write(str(e))
            sys.stderr.write(
                'There was a problem when getting the list of commits in the interval %s..%s\n' % (other_commit.id()[0], self._id))
            return out

        if match:
            out = [l.strip() for l in out if re.match(match, l)]
        else:
            out = [l.strip() for l in out ]

        return out


    def get_hunks(self, grouped=False):

        def is_hunk_line(line):
            return line[0] in '-+' and (len(line) < 2 or (line[1] != line[0]))

        def flatten_groups(hunk_groups):
            hunks = []
            for group in hunk_groups:
                for h in group:
                    hunks.append(h)
            return hunks

        def is_new_file(l):
            return (l[0:11] == 'diff --git ')

        if 'hunks' not in  self._attributes:
            self._attributes['hunks'] = []

            diff_lines = self.get_diff()
            # pprint(diff_lines)

            first_line_of_current_hunk = -1
            current_group = []
            line_no = 0
            for line_no, line in enumerate(diff_lines):
                # print(line_no, line)
                if is_new_file(line):
                    if len(current_group) > 0:
                        self._attributes['hunks'].append(current_group)
                        current_group = []
                        first_line_of_current_hunk = -1

                elif is_hunk_line(line):
                    if first_line_of_current_hunk == -1:
                        # print('first_line_of_current_hunk', line_no)
                        first_line_of_current_hunk = line_no
                else:
                    if first_line_of_current_hunk != -1:
                        current_group.append((first_line_of_current_hunk, line_no))
                        first_line_of_current_hunk = -1

            if first_line_of_current_hunk != -1:
                # wrap up hunk that ends at the end of the patch
                # print('line_no:', line_no)
                current_group.append((first_line_of_current_hunk, line_no + 1))

            self._attributes['hunks'].append(current_group)

        if grouped:
            return self._attributes['hunks']
        else:
            return flatten_groups(self._attributes['hunks'])

    # def timingInfo(self):
    #     return self._repository._commit_timing_data(self._id, self._verbose)

    def equals(self, other_commit):
        '''
        Return true if the two commits contain the same changes (despite different commit messages)
        '''
        return self.get_fingerprint() == other_commit.get_fingerprint()

    def get_fingerprint(self):
        if 'fingerprint' not in self._attributes:
            # try:
            cmd = [ 'git', 'show', '--format="%t"', '--numstat', self._id ]
            out = self._exec.run(cmd)
            self._attributes['fingerprint'] = hashlib.md5('\n'.join(out).encode()).hexdigest()
            # except: # pragma: no cover
            #     print('Failed to obtain fingerprint for commit: %s in dir: %s' % (self._id, self._exec._workdir))
            #     self._fingerprint = None

        return self._attributes['fingerprint']


    def _get_timing_data(self):
        data = self.get_timing_data()
        self._attributes['next_tag'] = data[0]
        # self._next_tag = data[0]

        self._attributes['next_tag_timestamp'] = data[1]
        # self._next_tag_timestamp = data[1]

        self._attributes['timestamp'] = data[2]
        # self._timestamp = data[2]

        self._attributes['time_to_tag'] = data[3]
        # self._time_to_tag = data[3]

    # TODO refactor
    # this method should become private and should be invoked to initialize (lazily)
    # the relevant attributes.
    def get_timing_data(self):
        # print("WARNING: deprecated method Commit::timing_data(), use Commit::get_next_tag() instead.")
        # if not os.path.exists(self._path):
        #     print('Folder ' + self._path + ' must exist!')
        #     return None

        # get tag info
        raw_out = self._exec.run('git tag --sort=taggerdate --contains ' + self._id) #,  cwd=self._path)
        if raw_out:
            tag = raw_out[0]
            tag_timestamp = self._exec.run('git show -s --format="%at" ' + tag + '^{commit}')[0][1:-1]
        else:
            tag = ''
            tag_timestamp = '0'

        try:
            commit_timestamp =  self._exec.run('git show -s --format="%ct" ' + self._id)[0][1:-1]
            time_delta = int(tag_timestamp) - int(commit_timestamp)
            if time_delta < 0:
                time_delta = -1
        except:
            commit_timestamp = '0'
            time_delta = 0

        tag_date = datetime.utcfromtimestamp(int(tag_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        commit_date = datetime.utcfromtimestamp(int(commit_timestamp)).strftime('%Y-%m-%d %H:%M:%S')

        if self._verbose:
            print('repository:                 ' + self._repository._url)
            print('commit:                     ' + self._id)
            print('commit_date:                ' + commit_timestamp)
            print('                            ' + commit_date)
            print('tag:                        ' + tag)
            print('tag_timestamp:              ' + tag_timestamp)
            print('                            ' + tag_date)
            print('Commit-to-release interval: {0:.2f} days'.format( time_delta/(3600 * 24) ))

        self._timestamp = commit_timestamp
        return (tag, tag_timestamp, commit_timestamp, time_delta )

    def get_tags(self):
        if 'tags' not in self._attributes:
            cmd = 'git tag --contains ' + self._id
            tags = self._exec.run(cmd)
            if not tags:
                self._attributes['tags'] = []
            else:
                self._attributes['tags'] = tags

        return self._attributes['tags']

    def get_next_tag(self):
        if 'next_tag' not in self._attributes:
            self._get_timing_data()
        return (self._attributes['next_tag'], self._attributes['next_tag_timestamp'], self._attributes['time_to_tag'])

    def __str__(self):
        data = (self._id,
                self.get_timestamp(date_format='%Y-%m-%d %H:%M:%S'),
                self.get_timestamp(),
                self._repository.get_url(),
                self.get_msg()[0],
                len(self.get_hunks()),
                len(self.get_changed_paths()),
                self.get_next_tag()[0],
                ', '.join(self.get_tags()),
                '\n'.join(self.get_changed_paths())
        )
        return "Commit id:         {}\nDate (timestamp):  {} ({})\nRepository:        {}\nMessage:           {}\nhunks: {},  changed files: {},  (oldest) tag: {}\ntags: {}\n{}".format(*data)


# class FilterCriterion():
#     def __init__(self, afterDate=None, beforeDate=None):
#         self._criteria = {
#             'beforeDate' : beforeDate,
#             'afterDate' : afterDate
#         }

#     def apply(self, commit):

#         # print('commit._timestamp:', commit.timestamp())
#         if self._criteria['beforeDate']:
#             # print('self._criteria["beforeDate"]', self._criteria['beforeDate'])
#             if commit.timestamp() > self._criteria['beforeDate']:
#                 # print('Not matching beforeDate')
#                 return False

#         if self._criteria['afterDate']:
#             # print('self._criteria["afterDate"]', self._criteria['afterDate'])
#             if commit.timestamp() < self._criteria['afterDate']:
#                 # print('Not matching afterDate')
#                 return False
#         print('Match!', commit.id())
#         return True

class CommitSet:
    def __init__(self, repo=None, commit_ids = [], prefetch=False, index=False):

        if repo is not None:
            self._repository = repo
        else:
            raise ValueError # pragma: no cover

        self._commits = []

        # TODO when the flag 'prefetch' is True, fetch all data in one shot (one single
        # call to the git binary) and populate all commit objects. A dictionary paramenter
        # passed to the Commit constructor will be used to pass the fields that need to be populated
        commits_count = len(commit_ids)
        if prefetch is True and commits_count > 50:
            print("WARNING: processing %d commits will take some time!" % commits_count)
            for cid in commit_ids:
                commit_data = {
                    'id': '',
                    'msg' : '',
                    'patch': '',
                    'timestamp': ''
                }
                current_field = None
                commit_raw_data = self._repository._exec.run('git show --format=@@@@@SHA1@@@@@%n%H%n@@@@@LOGMSG@@@@@%n%s%n%b%n@@@@@TIMESTAMP@@@@@@%n%at%n@@@@@PATCH@@@@@ ' + cid)

                for line in commit_raw_data:
                    if line == '@@@@@SHA1@@@@@':
                        current_field = 'id'
                    elif line == '@@@@@LOGMSG@@@@@':
                        current_field = 'msg'
                    elif line == '@@@@@TIMESTAMP@@@@@':
                        current_field = 'timestamp'
                    else:
                        commit_data[current_field] += '\n' + line

                self._commits.append(Commit(self._repository, cid, init_data=commit_data))
        else:
            self._commits = [Commit(self._repository, c) for c in commit_ids]

        # self._fingerprints = dict()
        # if index:
        #     self.index()

    # def index(self):
    #     for c in self._commits:
    #         fp = c.get_fingerprint()
    #         if fp in self._fingerprints:
    #             self._fingerprints[fp].append(c._id)
    #         else:
    #             self._fingerprints[fp] = [c._id]

    def get_all(self):
        return self._commits

    def add(self, commit_id):
        self._commits.append(Commit(self._repository, commit_id))
        return self

    # def get_duplicates(self):
    #     results = []
    #     # pprint(self._fingerprints)
    #     for k in self._fingerprints:
    #         if len(self._fingerprints[k]) > 1:
    #             results.append(self._fingerprints[k])
    #     return results

        # for c in self._commits:
        #     for d in self._commits:
        #         if c._id != d._id:
        #             if c.fingerprint() == d.fingerprint():
        #                 self._fingerprints[c._id].append(d)

    def filter_by_msg(self, word):
        # results = []
        # for c in self.get_all():
        #     if criterion.apply(c):
        #         results.append(c)

        return [ c for c in self.get_all() if word in c.get_msg()]

        # return results
