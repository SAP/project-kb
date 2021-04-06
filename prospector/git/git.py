# -*- coding: utf-8 -*-

import subprocess
import multiprocessing
import logging
import os
import sys
import shutil
import random
import re
import difflib
import hashlib

# from pprint import pprint
# import pickledb

from datetime import datetime

GIT_CACHE = ""
if "GIT_CACHE" in os.environ:
    GIT_CACHE = os.environ["GIT_CACHE"]

if not os.path.isdir(GIT_CACHE):
    raise ValueError(
        "Environment variable GIT_CACHE is not set or it points to a directory that does not exist"
    )


def sample_func(s, z):
    res = dict()
    res["value"] = len(s + z)
    return res


def do_clone(url, output_folder, shallow=False, skip_existing=False):
    git = Git(url, cache_path=output_folder, shallow=shallow)
    git.clone(shallow=shallow, skip_existing=skip_existing)
    return str(len(git.get_commits()))


def clone_repo_multiple(
    url_list,
    output_folder,
    proxy="",
    shallow=False,
    skip_existing=False,
    concurrent=multiprocessing.cpu_count(),
):
    """
    This is the parallelized version of clone_repo (works with a list of repositories).
    """
    print("Using {} parallel workers".format(concurrent))
    with multiprocessing.Pool(concurrent) as pool:
        args = ((url, output_folder, proxy, shallow, skip_existing) for url in url_list)
        results = pool.starmap(do_clone, args)

    return results


class Git:
    def __init__(
        self,
        url,
        cache_path=os.path.abspath("/tmp/git-cache"),
        verbose=False,
        shallow=False,
    ):
        self.repository_type = "GIT"
        self._verbose = verbose
        self._url = url
        self._path = os.path.join(cache_path, self._url.rstrip("/").split("/")[-1])
        # self._path = os.path.join(cache_path, self._url.replace("https://","").replace("/", "_"))
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
        """
        Identifies the default branch of the remote repository for the local git
        repo
        """
        logging.info("Identifiying remote branch for " + self._path)

        try:
            cmd = "git ls-remote -q"
            # self._exec._encoding = 'utf-8'
            l_raw_output = self._exec.run(cmd)

            logging.info(
                "Identifiying sha1 of default remote ref among {} entries.".format(
                    len(l_raw_output)
                )
            )

            for raw_line in l_raw_output:
                if not raw_line:
                    continue
                (sha1, ref_name) = raw_line.split("\t")

                if ref_name == "HEAD":
                    head_sha1 = sha1
                    logging.info("Remote head: " + sha1)
                    break

        except subprocess.CalledProcessError as ex:
            logging.error(
                "Exception happened while obtaining default remote branch for repository in "
                + self._path
            )
            logging.error(str(ex))
            return None

        # ...then search the corresponding treeish among the local references
        try:
            cmd = "git show-ref"
            # self._exec._encoding = 'utf-8'
            l_raw_output = self._exec.run(cmd)

            logging.info("Processing {} references".format(len(l_raw_output)))

            for raw_line in l_raw_output:
                (sha1, ref_name) = raw_line.split()
                if sha1 == head_sha1:
                    return ref_name
            return None

        except Exception as ex:
            logging.error(
                "Exception happened while obtaining default remote branch for repository in "
                + self._path
            )
            logging.error(str(ex))
            return None

    def clone(self, shallow=None, skip_existing=False):
        """
        Clones the specified repository checking out the default branch in a subdir of output_folder.
        Shallow=true speeds up considerably the operation, but gets no history.
        """
        if shallow:
            self._shallow_clone = shallow

        if not self._url:
            print("Invalid url specified.")
            sys.exit(-1)

        # TODO rearrange order of checks
        if os.path.isdir(os.path.join(self._path, ".git")):
            if skip_existing:
                if self._verbose:
                    print("Skipping fetch of {} in {}".format(self._url, self._path))
            else:
                if self._verbose:
                    print(
                        "\nFound repo {} in {}.\nFetching....".format(
                            self._url, self._path
                        )
                    )

                self._exec.run(["git", "fetch", "--progress", "--all", "--tags"])
                # , cwd=self._path, timeout=self._exec_timeout)
            return

        if os.path.exists(self._path):
            if self._verbose:
                print(
                    "Folder {} exists but it contains no git repository.".format(
                        self._path
                    )
                )
            return

        os.makedirs(self._path)

        if self._verbose:
            print("Cloning %s (shallow=%s)" % (self._url, self._shallow_clone))

        if not self._exec.run(["git", "init"], ignore_output=True):
            print("Failed to initialize repository in %s" % self._path)

        try:
            self._exec.run(
                ["git", "remote", "add", "origin", self._url], ignore_output=True
            )
            #  , cwd=self._path)
        except Exception as ex:
            print("Could not update remote in %s (%s)" % (self._path, str(ex)))
            shutil.rmtree(self._path)
            raise ex

        try:
            if self._shallow_clone:
                self._exec.run(["git", "fetch", "--depth", "1"])  # , cwd=self._path)
                # sh.git.fetch('--depth', '1', 'origin', _cwd=self._path)
            else:
                # sh.git.fetch('--all', '--tags', _cwd=self._path)
                self._exec.run(
                    ["git", "fetch", "--progress", "--all", "--tags"]
                )  # , cwd=self._path)
                # self._exec.run_l(['git', 'fetch', '--tags'], cwd=self._path)
        except Exception as ex:
            print(
                "Could not fetch %s (shallow=%s) in %s"
                % (self._url, str(self._shallow_clone), self._path)
            )
            shutil.rmtree(self._path)
            raise ex

    def get_commits(
        self,
        ancestors_of=None,
        exclude_ancestors_of=None,
        since=None,
        until=None,
        filter_files="",
        find_in_code="",
        find_in_msg="",
    ):
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
            cmd.append("^" + exclude_ancestors_of)

        if filter_files:
            cmd.append(filter_files)

        if find_in_code:
            cmd.append('-S"%s"' % find_in_code)

        if find_in_msg:
            cmd.append('--grep="%s"' % find_in_msg)

        try:
            print(" ".join(cmd))
            out = self._exec.run(cmd)
        except Exception as ex:
            sys.stderr.write("Git command failed, cannot get commits \n%s" % str(ex))
            out = []

        out = [l.strip() for l in out]
        return out

    def get_commit(self, key, by="id"):
        if by == "id":
            return Commit(self, key, self._verbose)
        if by == "fingerprint":
            # TODO implement computing fingerprints
            c_id = self._fingerprints[key]
            return Commit(self, c_id, self._verbose)

        return None

    def get_random_commits(self, count):
        """
        Return a list of n random commits from repo, which is assumed to be available
        as a standard-named subdirectory of base_dir
        """
        return reservoir_sampling(self.get_commits(), count)

    def get_tag_for_version(self, version):
        """
        get closest match from tags, given the version id
        """
        # return Levenshtein.ratio('hello world', 'hello')
        version = re.sub("[^0-9]", "", version)

        tags = self.get_tags()
        best_match = ("", 0.0)
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
            tags = self._exec.run("git tag")
        except subprocess.CalledProcessError as exc:
            print("Git command failed." + str(exc.output))
            tags = []

        if not tags:
            tags = []

        return tags

    def get_commit_id_for_tag(self, tag):
        cmd = "git rev-list -n1 " + tag
        cmd = cmd.split()

        try:
            # @TODO: https://stackoverflow.com/questions/16198546/get-exit-code-and-stderr-from-subprocess-call
            commit_id = subprocess.check_output(cmd, cwd=self._path).decode()
        except subprocess.CalledProcessError as exc:
            print("Git command failed." + str(exc.output))
            sys.exit(1)
        if not commit_id:
            return None
        return commit_id.strip()

    def get_previous_tag(self, tag):
        # https://git-scm.com/docs/git-describe
        commit_for_tag = self.get_commit_id_for_tag(tag)
        cmd = "git describe --abbrev=0 --all --tags --always " + commit_for_tag + "^"
        cmd = cmd.split()

        try:
            # @TODO: https://stackoverflow.com/questions/16198546/get-exit-code-and-stderr-from-subprocess-call
            tags = self._exec.run(cmd)
        except subprocess.CalledProcessError as exc:
            print("Git command failed." + str(exc.output))
            return []

        if not tags:
            return []

        return tags


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

    def get_id(self):
        if "full_id" not in self._attributes:
            try:
                cmd = ["git", "log", "--format=%H", "-n1", self._id]
                self._attributes["full_id"] = self._exec.run(cmd)[0]
            except:
                print(
                    "Failed to obtain full commit id for: %s in dir: %s"
                    % (self._id, self._exec._workdir)
                )
        return (self._id, self._attributes["full_id"])

    def get_msg(self):
        if "msg" not in self._attributes:
            self._attributes["msg"] = ""
            try:
                cmd = ["git", "log", "--format=%B", "-n1", self._id]
                self._attributes["msg"] = " ".join(self._exec.run(cmd))
            except:
                print(
                    "Failed to obtain commit message for commit: %s in dir: %s"
                    % (self._id, self._exec._workdir)
                )
        return self._attributes["msg"]

    def get_diff(self, context_size=1, filter_files=""):
        if "diff" not in self._attributes:
            self._attributes["diff"] = ""
            try:
                cmd = [
                    "git",
                    "diff",
                    "--unified=" + str(context_size),
                    self._id + "^.." + self._id,
                ]
                if filter_files:
                    cmd.append(filter_files)
                self._attributes["diff"] = self._exec.run(cmd)
            except:
                print(
                    "Failed to obtain patch for commit: %s in dir: %s"
                    % (self._id, self._exec._workdir)
                )
        return self._attributes["diff"]

    def get_timestamp(self, date_format=None):
        if "timestamp" not in self._attributes:
            self._attributes["timestamp"] = None
            self._get_timing_data()
            # self._timestamp = self.timing_data()[2]
        if date_format:
            return datetime.utcfromtimestamp(
                int(self._attributes["timestamp"])
            ).strftime(date_format)
        return self._attributes["timestamp"]

    def get_changed_files(self):
        if "changed_files" not in self._attributes:
            cmd = ["git", "diff", "--name-only", self._id + "^.." + self._id]
            out = self._exec.run(cmd)
            self._attributes["changed_files"] = out
        return self._attributes["changed_files"]

    def get_changed_paths(self, other_commit=None, match=None):
        # TODO refactor, this overlaps with changed_files

        if other_commit is None:
            other_commit_id = self._id + "^"
        else:
            other_commit_id = other_commit._id

        cmd = [
            "git",
            "log",
            "--name-only",
            "--format=%n",
            "--full-index",
            other_commit_id + ".." + self._id,
        ]
        try:
            out = self._exec.run(cmd)
        except Exception as e:
            out = str()
            sys.stderr.write(str(e))
            sys.stderr.write(
                "There was a problem when getting the list of commits in the interval %s..%s\n"
                % (other_commit.id()[0], self._id)
            )
            return out

        if match:
            out = [l.strip() for l in out if re.match(match, l)]
        else:
            out = [l.strip() for l in out]

        return out

    def get_hunks(self, grouped=False):
        def is_hunk_line(line):
            return line[0] in "-+" and (len(line) < 2 or (line[1] != line[0]))

        def flatten_groups(hunk_groups):
            hunks = []
            for group in hunk_groups:
                for h in group:
                    hunks.append(h)
            return hunks

        def is_new_file(l):
            return l[0:11] == "diff --git "

        if "hunks" not in self._attributes:
            self._attributes["hunks"] = []

            diff_lines = self.get_diff()
            # pprint(diff_lines)

            first_line_of_current_hunk = -1
            current_group = []
            line_no = 0
            for line_no, line in enumerate(diff_lines):
                # print(line_no, line)
                if is_new_file(line):
                    if len(current_group) > 0:
                        self._attributes["hunks"].append(current_group)
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

            self._attributes["hunks"].append(current_group)

        if grouped:
            return self._attributes["hunks"]
        else:
            return flatten_groups(self._attributes["hunks"])

    def equals(self, other_commit):
        """
        Return true if the two commits contain the same changes (despite different commit messages)
        """
        return self.get_fingerprint() == other_commit.get_fingerprint()

    def get_fingerprint(self):
        if "fingerprint" not in self._attributes:
            # try:
            cmd = ["git", "show", '--format="%t"', "--numstat", self._id]
            out = self._exec.run(cmd)
            self._attributes["fingerprint"] = hashlib.md5(
                "\n".join(out).encode()
            ).hexdigest()

        return self._attributes["fingerprint"]

    def _get_timing_data(self):
        data = self.get_timing_data()
        self._attributes["next_tag"] = data[0]
        # self._next_tag = data[0]

        self._attributes["next_tag_timestamp"] = data[1]
        # self._next_tag_timestamp = data[1]

        self._attributes["timestamp"] = data[2]
        # self._timestamp = data[2]

        self._attributes["time_to_tag"] = data[3]
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
        raw_out = self._exec.run(
            "git tag --sort=taggerdate --contains " + self._id
        )  # ,  cwd=self._path)
        if raw_out:
            tag = raw_out[0]
            tag_timestamp = self._exec.run(
                'git show -s --format="%at" ' + tag + "^{commit}"
            )[0][1:-1]
        else:
            tag = ""
            tag_timestamp = "0"

        try:
            commit_timestamp = self._exec.run('git show -s --format="%ct" ' + self._id)[
                0
            ][1:-1]
            time_delta = int(tag_timestamp) - int(commit_timestamp)
            if time_delta < 0:
                time_delta = -1
        except:
            commit_timestamp = "0"
            time_delta = 0

        tag_date = datetime.utcfromtimestamp(int(tag_timestamp)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        commit_date = datetime.utcfromtimestamp(int(commit_timestamp)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if self._verbose:
            print("repository:                 " + self._repository._url)
            print("commit:                     " + self._id)
            print("commit_date:                " + commit_timestamp)
            print("                            " + commit_date)
            print("tag:                        " + tag)
            print("tag_timestamp:              " + tag_timestamp)
            print("                            " + tag_date)
            print(
                "Commit-to-release interval: {0:.2f} days".format(
                    time_delta / (3600 * 24)
                )
            )

        self._timestamp = commit_timestamp
        return (tag, tag_timestamp, commit_timestamp, time_delta)

    def get_tags(self):
        if "tags" not in self._attributes:
            cmd = "git tag --contains " + self._id
            tags = self._exec.run(cmd)
            if not tags:
                self._attributes["tags"] = []
            else:
                self._attributes["tags"] = tags

        return self._attributes["tags"]

    def get_next_tag(self):
        if "next_tag" not in self._attributes:
            self._get_timing_data()
        return (
            self._attributes["next_tag"],
            self._attributes["next_tag_timestamp"],
            self._attributes["time_to_tag"],
        )

    def __str__(self):
        data = (
            self._id,
            self.get_timestamp(date_format="%Y-%m-%d %H:%M:%S"),
            self.get_timestamp(),
            self._repository.get_url(),
            self.get_msg()[0],
            len(self.get_hunks()),
            len(self.get_changed_paths()),
            self.get_next_tag()[0],
            ", ".join(self.get_tags()),
            "\n".join(self.get_changed_paths()),
        )
        return "Commit id:         {}\nDate (timestamp):  {} ({})\nRepository:        {}\nMessage:           {}\nhunks: {},  changed files: {},  (oldest) tag: {}\ntags: {}\n{}".format(
            *data
        )


class CommitSet:
    def __init__(self, repo=None, commit_ids=[], prefetch=False, index=False):

        if repo is not None:
            self._repository = repo
        else:
            raise ValueError  # pragma: no cover

        self._commits = []

        # TODO when the flag 'prefetch' is True, fetch all data in one shot (one single
        # call to the git binary) and populate all commit objects. A dictionary paramenter
        # passed to the Commit constructor will be used to pass the fields that need to be populated
        commits_count = len(commit_ids)
        if prefetch is True and commits_count > 50:
            print("WARNING: processing %d commits will take some time!" % commits_count)
            for cid in commit_ids:
                commit_data = {"id": "", "msg": "", "patch": "", "timestamp": ""}
                current_field = None
                commit_raw_data = self._repository._exec.run(
                    "git show --format=@@@@@SHA1@@@@@%n%H%n@@@@@LOGMSG@@@@@%n%s%n%b%n@@@@@TIMESTAMP@@@@@@%n%at%n@@@@@PATCH@@@@@ "
                    + cid
                )

                for line in commit_raw_data:
                    if line == "@@@@@SHA1@@@@@":
                        current_field = "id"
                    elif line == "@@@@@LOGMSG@@@@@":
                        current_field = "msg"
                    elif line == "@@@@@TIMESTAMP@@@@@":
                        current_field = "timestamp"
                    else:
                        commit_data[current_field] += "\n" + line

                self._commits.append(
                    Commit(self._repository, cid, init_data=commit_data)
                )
        else:
            self._commits = [Commit(self._repository, c) for c in commit_ids]

    def get_all(self):
        return self._commits

    def add(self, commit_id):
        self._commits.append(Commit(self._repository, commit_id))
        return self

    def filter_by_msg(self, word):
        return [c for c in self.get_all() if word in c.get_msg()]


class Exec:
    def __init__(self, workdir=None, encoding="latin-1", timeout=None):
        self._encoding = encoding
        self._timeout = timeout
        self.setDir(workdir)

    def setDir(self, path):
        if os.path.isabs(path):
            self._workdir = path
        else:
            raise ValueError("Path must be absolute for Exec to work: " + path)

    def run(self, cmd, ignore_output=False):
        if isinstance(cmd, str):
            cmd = cmd.split()

        if ignore_output:
            self._execute_no_output(cmd)
            return []

        result = self._execute(cmd)
        if result is None:
            return []

        return result

    def _execute_no_output(self, cmd_l):
        try:
            subprocess.check_call(
                cmd_l,
                cwd=self._workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:  # pragma: no cover
            print("Timeout exceeded (" + self._timeout + " seconds)")
            raise Exception("Process did not respond for " + self._timeout + " seconds")

    def _execute(self, cmd_l):
        try:
            proc = subprocess.Popen(cmd_l, cwd=self._workdir, stdout=subprocess.PIPE)
            out, err = proc.communicate()

            if proc.returncode != 0:
                raise Exception(
                    "Process (%s) exited with non-zero return code" % " ".join(cmd_l)
                )
            # if err:       # pragma: no cover
            #     traceback.print_exc()
            #     raise Exception('Execution failed')

            raw_output_list = out.decode(self._encoding).split("\n")
            return [r for r in raw_output_list if r.strip() != ""]
        except subprocess.TimeoutExpired:  # pragma: no cover
            print("Timeout exceeded (" + self._timeout + " seconds)")
            raise Exception("Process did not respond for " + self._timeout + " seconds")
            # return None
        # except Exception as ex:                 # pragma: no cover
        #     traceback.print_exc()
        #     raise ex


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


# LEGACY CODE
#
# The following functions implement the heuristic to map a string version
# such as "2.3.35" onto a tag such as "STRUTS_2_3_35"


def version_to_wide_interval_tags(version, git_repo, tag_margin=1):
    """
    A version is mapped onto a tag, and a tuple of a wide version interval is returned
        [0] corresponds to the previous tag
        [1] corresponds to the next tag

    Input:
        version (str): the version
        git_repo (git_explorer.GIT):
        tag_margin (int): how wide the interval can be

    Returns:
        # tuple: previous tag, next tag
        list: for every tag, returns a tuple with previous tag, current next tag
        @TODO: return only one tuple: previous tag, next tag
    """
    result = list()
    tags = git_repo.get_tags()

    # can return multiple tags now, as matching is not perfect
    for tag in get_tag_for_version(tags, version):

        tag_timestamp = get_timestamp_for_tag(tag, git_repo)

        previous_tag = find_previous_tag(tag, tags, tag_timestamp, git_repo)
        if previous_tag == None:
            if tags.index(tag) != 0:
                previous_tag = tags[tags.index(tag) - 1]
            else:
                previous_tag = tags[tags.index(tag)]

        for i in range(tag_margin - 1):
            # when no valid new version has been found but the current version is in the tags
            possible_previous_tag = find_previous_tag(
                previous_tag, tags, tag_timestamp, git_repo
            )
            if possible_previous_tag == None:
                break
            else:
                previous_tag = possible_previous_tag

        next_tag = find_next_tag(tag, tags, tag_timestamp, git_repo)
        if next_tag == None:
            if tags.index(tag) != len(tags) - 1:
                next_tag = tags[tags.index(tag) + 1]
            else:
                next_tag = tags[tags.index(tag)]

        for i in range(tag_margin - 1):
            possible_next_tag = find_next_tag(next_tag, tags, tag_timestamp, git_repo)
            if possible_next_tag == None:
                break
            else:
                next_tag = possible_next_tag

        if (previous_tag, tag) not in result:
            result.append((previous_tag, tag))
        if (tag, next_tag) not in result:
            result.append((tag, next_tag))
    return result


def find_next_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
    """
    Tries to find the next tag by means of incrementing digits in the tag

    Input:
        tag (str): the tag
        tags (list): all tags
        (digit_indices should not be provided, is used for the recursion)
        (loop does not have to be provided, is used for the recursion)

    Returns:
        str: the next tag
    """
    if type(tags) != list or len(tags) == 0:
        raise ValueError(
            "tags should be a list of tags to map the version onto, is a {} of length {}".format(
                type(tags), len(tags)
            )
        )
    if type(git_repo) != Git:
        raise TypeError(
            "git-repo should be of type git_explorer.core.Git, not {}".format(
                type(git_repo)
            )
        )

    # splits the tag into a list of integers and strings
    splitted_tag = recursively_split_version_string(tag, [])

    # determines which indices in the list correspond to digits of the version number
    if digit_indices == None:
        if tag_timestamp == None:
            tag_timestamp = get_timestamp_for_tag(tag, git_repo)
        digit_indices = list(
            reversed(
                [index for index, val in enumerate(splitted_tag) if type(val) == int]
            )
        )
        loop = 0

    # searching for valid tags: recursively to evaluate different
    tried_indices = []
    for index in digit_indices:

        # as we're looking for the next tag, it is unlikely that there will be a gap of more than 10
        for i in range(10):
            splitted_tag[index] += 1

            possible_tag = "".join([str(x) for x in splitted_tag])

            if possible_tag in tags:
                possible_tag_timestamp = get_timestamp_for_tag(possible_tag, git_repo)
                if tag_timestamp < possible_tag_timestamp:
                    return possible_tag

            if len(tried_indices) != 0:
                result = find_next_tag(
                    possible_tag, tags, tag_timestamp, git_repo, tried_indices, loop + 1
                )
                if result:
                    return result

        # when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.9
        splitted_tag[index] = 0
        tried_indices.append(index)

    # when every combination is tried, chop off the last part of the tag
    if loop == 0 and len(tag) > 1:
        shortened_tag = "".join(
            [str(x) for x in recursively_split_version_string(tag, [])[:-1]]
        )
        return find_next_tag(shortened_tag, tags, tag_timestamp, git_repo)

    # None is returned when there is no match
    return


def find_previous_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
    """
    Tries to find the previous tag by means of decrementing digits in the tag,
        and checking whether the new tag exists. It starts at the last digit and works it way back.
        When all digits have become 0, the last element of tag is removed and the process is tried again.

    Input:
        tag (str): the tag
        tags (list): all tags
        (digit_indices should not be provided, is used for the recursion)

    Returns:
        str: the previous tag
    """
    if type(tags) != list or len(tags) == 0:
        raise ValueError(
            "tags should be a list of tags to map the version onto, is a {} of length {}".format(
                type(tags), len(tags)
            )
        )
    if type(git_repo) != Git:
        raise TypeError(
            "git-repo should be of type git_explorer.core.Git, not {}".format(
                type(git_repo)
            )
        )

    # splits the tag into a list of integers and strings
    splitted_tag = recursively_split_version_string(tag, [])

    # determines which indices in the list correspond to digits of the version number
    if digit_indices == None:
        if tag_timestamp == None:
            tag_timestamp = get_timestamp_for_tag(tag, git_repo)
        loop = 0
        digit_indices = list(
            reversed(
                [index for index, val in enumerate(splitted_tag) if type(val) == int]
            )
        )

    # searching for valid tags: recursively to evaluate different
    tried_indices = []
    for index in digit_indices:

        i = 0
        # sometimes a date is used (thus takes a long time)
        if splitted_tag[index] < 100:
            while splitted_tag[index] > 0:
                i += 1
                splitted_tag[index] -= 1

                possible_tag = "".join([str(x) for x in splitted_tag])

                if possible_tag in tags:
                    possible_tag_timestamp = get_timestamp_for_tag(
                        possible_tag, git_repo
                    )
                    if tag_timestamp > possible_tag_timestamp:
                        return possible_tag

                if len(tried_indices) != 0:
                    result = find_previous_tag(
                        possible_tag,
                        tags,
                        tag_timestamp,
                        git_repo,
                        tried_indices,
                        loop + 1,
                    )
                    if result:
                        return result

        # when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.99
        splitted_tag[index] = 99
        tried_indices.append(index)

    # when every combination is tried, chop off the last part of the tag
    if loop == 0 and len(tag) > 1:
        shortened_tag = "".join(
            [str(x) for x in recursively_split_version_string(tag, [])[:-1]]
        )
        # print(shortened_tag)
        return find_previous_tag(shortened_tag, tags, tag_timestamp, git_repo)
    return


def recursively_split_version_string(input_version, output_version=[]):
    """
    Splits a version/tag string into a list with integers and strings
        i.e. "8.0.0.RC10" --> [8, '.', 0, '.', 0, '.RC', 10]

    Input:
        input_version (str): a version or tag i.e. "8.0.0.RC10"
        output_version (list): an empty list, which will be filled iteratively

    Returns:
        list: the version/tag string in a list with integers and strings i.e. [8, '.', 0, '.', 0, '.RC', 10]
    """
    if type(input_version) != str:
        raise TypeError(
            "The provided version should be a str data type but is of type {}.".format(
                type(input_version)
            )
        )

    # when the part to split is only digits or no digits at all, the process is finished
    if (
        input_version.isdigit()
        or any(char.isdigit() for char in input_version) == False
    ):
        version = output_version + [input_version]
        return [
            int(character) if character.isdigit() else character
            for character in version
        ]

    # otherwise check until what position it is a digit (since we want to keep i.e. a multiple digits number as one integer)
    pos = 0
    while (
        input_version[pos].isdigit() == input_version[pos + 1].isdigit()
        and pos != len(input_version) - 2
    ):  #
        pos += 1

    return recursively_split_version_string(
        input_version[pos + 1 :], output_version + [input_version[: pos + 1]]
    )


def get_timestamp_for_tag(tag, git_repo):
    """
    Retreive the timestamp the tag was created.

    Input:
        repo_url (str): the repository where the tag can be found
        tag (str): the tag

    Return:
        int: timestamp (use datetime.fromtimestamp(timestamp) for datetime)
    """
    if type(git_repo) != Git:
        raise TypeError(
            "git-repo should be of type git_explorer.core.Git, not {}".format(
                type(git_repo)
            )
        )
    if type(tag) != str:
        raise TypeError("tag must be str, not {}".format(type(tag)))
    if tag not in git_repo.get_tags():
        raise ValueError("tag {} not found in git_repo".format(tag))

    commit_id = git_repo.get_commit_id_for_tag(tag)
    commit = Commit(git_repo, commit_id)
    return int(commit.get_timestamp())


def get_tag_for_version(tags, version):
    """
    Map a version onto an existing tag

    Input: tags (list): a list of tags to map version onto version (str): the
        version

    Returns: list: list with tags that could be the version

        TODO: only return
        the most relevant tag i.e. for key 8 version 4.1 returns
        ['version-3.4.1', 'version-4.1', 'version-4.4.1']
    """
    if type(tags) != list or len(tags) == 0:
        raise ValueError(
            "tags should be a list of tags to map the version onto, is a {} of length {}".format(
                type(tags), len(tags)
            )
        )

    # stripped_tags = [tag[len(tag)-len(version):] for tag in tags]
    stripped_tags = [
        tag[
            tag.index(
                [
                    str(value)
                    for value in recursively_split_version_string(tag)
                    if type(value) == int
                ][0]
            ) :
        ]
        if any(char.isdigit() for char in tag)
        else tag
        for tag in tags
    ]
    stripped_version = (
        version[
            version.index(
                [
                    str(value)
                    for value in recursively_split_version_string(version)
                    if type(value) == int
                ][0]
            ) :
        ]
        if any(char.isdigit() for char in version)
        else version
    )

    if version in tags and tags.count(version) == 1:
        tag = version
    elif version in stripped_tags and stripped_tags.count(version) == 1:
        tag = tags[stripped_tags.index(version)]
    elif version in stripped_tags and stripped_tags.count(version) > 1:
        return [
            tags[index] for index, tag in enumerate(stripped_tags) if tag == version
        ]
    elif (
        stripped_version in stripped_tags and stripped_tags.count(stripped_version) == 1
    ):
        tag = tags[stripped_tags.index(stripped_version)]
    elif (
        stripped_version in stripped_tags and stripped_tags.count(stripped_version) > 1
    ):
        return [
            tags[index]
            for index, tag in enumerate(stripped_tags)
            if tag == stripped_version
        ]

    else:
        version = re.sub("[^0-9]", "", version)
        best_match = ("", 0.0)
        for tag in tags:
            t_strip = re.sub("[^0-9]", "", tag)
            match_score = difflib.SequenceMatcher(None, t_strip, version).ratio()
            if match_score > best_match[1]:
                best_match = (tag, match_score)
        tag = best_match[0]
    return [tag]
