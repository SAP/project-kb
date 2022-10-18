# -*- coding: utf-8 -*-
# flake8: noqa

import difflib
import multiprocessing
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
from typing import Dict, List
from urllib.parse import urlparse

from git.exec import Exec
from git.raw_commit import RawCommit

from log.logger import logger

from stats.execution import execution_statistics, measure_execution_time

# If we don't parse .env file, we can't use the environment variables
# load_dotenv()

GIT_CACHE = os.getenv("GIT_CACHE")

FILTERING_EXTENSIONS = ["java", "c", "cpp", "py", "js", "go", "php", "h", "jsp"]


if not os.path.isdir(GIT_CACHE):
    raise ValueError(
        f"Environment variable GIT_CACHE is not set or it points to a directory that does not exist: {GIT_CACHE}"
    )


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
    logger.debug(f"Using {concurrent} parallel workers")
    with multiprocessing.Pool(concurrent) as pool:
        args = ((url, output_folder, proxy, shallow, skip_existing) for url in url_list)
        results = pool.starmap(do_clone, args)

    return results


def path_from_url(url: str, base_path):
    url = url.rstrip("/")
    parsed_url = urlparse(url)
    return os.path.join(
        base_path, parsed_url.netloc + parsed_url.path.replace("/", "_")
    )


def create_exec(workdir: str):
    return Exec(workdir=workdir)


class Git:
    def __init__(
        self,
        url,
        cache_path=os.path.abspath("/tmp/gitcache"),
        shallow=False,
    ):
        self.repository_type = "GIT"
        self.url = url
        self.path = path_from_url(url, cache_path)
        self.fingerprints = dict()
        self.exec_timeout = None
        self.shallow_clone = shallow
        self.exec = create_exec(self.path)
        self.storage = None

    def set_exec(self, exec_obj=None):
        return Exec(workdir=self.path)

    def execute(self, cmd: str, silent: bool = False):
        return self.exec.run(cmd, silent=silent, cache=True)

    def get_url(self):
        return self.url

    def get_default_branch(self):
        """
        Identifies the default branch of the remote repository for the local git
        repo
        """
        logger.debug("Identifiying remote branch for %s", self.path)

        try:
            cmd = "git ls-remote -q"
            # self.exec._encoding = 'utf-8'
            l_raw_output = self.execute(cmd)

            logger.debug(
                "Identifiying sha1 of default remote ref among %d entries.",
                len(l_raw_output),
            )

            for raw_line in l_raw_output:
                if not raw_line:
                    continue
                (sha1, ref_name) = raw_line.split("\t")

                if ref_name == "HEAD":
                    head_sha1 = sha1
                    logger.debug("Remote head: " + sha1)
                    break

        except subprocess.CalledProcessError as ex:
            logger.error(
                "Exception happened while obtaining default remote branch for repository in "
                + self.path
            )
            logger.error(str(ex))
            return None

        # ...then search the corresponding treeish among the local references
        try:
            cmd = "git show-ref"
            # self.exec._encoding = 'utf-8'
            l_raw_output = self.execute(cmd)

            logger.debug("Processing {} references".format(len(l_raw_output)))

            for raw_line in l_raw_output:
                (sha1, ref_name) = raw_line.split()
                if sha1 == head_sha1:
                    return ref_name
            return None

        except Exception as ex:
            logger.error(
                "Exception happened while obtaining default remote branch for repository in "
                + self.path
            )

            logger.error(str(ex))
            return None

    def clone(self, shallow=None, skip_existing=False):
        """
        Clones the specified repository checking out the default branch in a subdir of output_folder.
        Shallow=true speeds up considerably the operation, but gets no history.
        """
        if shallow:
            self.shallow_clone = shallow

        if not self.url:
            logger.error("Invalid url specified.")
            sys.exit(-1)

        # TODO rearrange order of checks
        if os.path.isdir(os.path.join(self.path, ".git")):
            if skip_existing:
                logger.debug(f"Skipping fetch of {self.url} in {self.path}")
            else:
                logger.debug(f"\nFound repo {self.url} in {self.path}.\nFetching....")

                self.execute("git fetch --progress --all --tags")
                # , cwd=self.path, timeout=self.exec_timeout)
            return

        if os.path.exists(self.path):
            logger.debug(
                "Folder {} exists but it contains no git repository.".format(self.path)
            )
            return

        os.makedirs(self.path)

        logger.debug(f"Cloning {self.url} (shallow={self.shallow_clone})")

        if not self.execute("git init", silent=False):
            logger.error(f"Failed to initialize repository in {self.path}")

        try:
            self.exec.run(
                f"git remote add origin {self.url}",
                silent=True,
            )
            #  , cwd=self.path)
        except Exception as ex:
            logger.error(f"Could not update remote in {self.path}", exc_info=True)
            shutil.rmtree(self.path)
            raise ex

        try:
            if self.shallow_clone:
                self.execute("git fetch --depth 1")  # , cwd=self.path)
                # sh.git.fetch('--depth', '1', 'origin', _cwd=self.path)
            else:
                # sh.git.fetch('--all', '--tags', _cwd=self.path)
                self.execute("git fetch --progress --all --tags")
                # , cwd=self.path)
                # self.exec.run_l(['git', 'fetch', '--tags'], cwd=self.path)
        except Exception as ex:
            logger.error(
                f"Could not fetch {self.url} (shallow={str(self.shallow_clone)}) in {self.path}",
                exc_info=True,
            )
            shutil.rmtree(self.path)
            raise ex

    @measure_execution_time(execution_statistics.sub_collection("core"))
    def create_commits(
        self,
        ancestors_of=None,
        exclude_ancestors_of=None,
        since=None,
        until=None,
        find_in_code="",
        find_in_msg="",
    ):
        cmd = "git rev-list"

        if ancestors_of is None:
            cmd += " --all"

        if since:
            cmd += f" --since={since}"

        if until:
            cmd += f" --until={until}"

            params["page"] += 1
            if params["page"] > 10:
                break
            r = requests.get(query_url, params=params, headers=headers)

    # @measure_execution_time(execution_statistics.sub_collection("core"))
    def get_commits(
        self,
        ancestors_of=None,
        exclude_ancestors_of=None,
        since=None,
        until=None,
        find_in_code="",
        find_in_msg="",
    ):
        cmd = "git log --format=%H"

        if ancestors_of is None:
            cmd += " --all"

        # by filtering the dates of the tags we can reduce the commit range safely (in theory)
        if ancestors_of:
            cmd += " " + str(ancestors_of)

        if exclude_ancestors_of:
            cmd += f" ^{exclude_ancestors_of}"

        for extension in FILTERING_EXTENSIONS:
            cmd += f" *.{extension}"

        # What is this??
        if find_in_code:
            cmd += f" -S{find_in_code}"

        if find_in_msg:
            cmd += f" --grep={find_in_msg}"

        try:
            logger.debug(cmd)
            out = self.execute(cmd)
        #     --cherry-mark
        # Like --cherry-pick (see below) but mark equivalent commits with =
        # rather than omitting them, and inequivalent ones with +.

        except Exception:
            logger.error("Git command failed, cannot get commits", exc_info=True)
            out = []

        return [l.strip() for l in out]

    def get_commits_between_two_commit(self, commit_from: str, commit_to: str):
        """
        Return the commits between the start commit and the end commmit if there are path between them or empty list
        """
        try:
            cmd = f"git rev-list --ancestry-path {commit_from}..{commit_to}"

            path = self.execute(cmd)  # ???
            if len(path) > 0:
                path.pop(0)
                path.reverse()
            return path
        except:
            logger.error("Failed to obtain commits, details below:", exc_info=True)
            return []

    @measure_execution_time(execution_statistics.sub_collection("core"))
    def get_commit(self, id):
        return RawCommit(self.url, id, self.exec)

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

    def extract_tag_timestamp(self, tag: str) -> int:
        out = self.execute(f"git log -1 --format=%at {tag}")
        return int(out[0])

    # Return the timestamp for given a version if version exist or None
    def extract_timestamp_from_version(self, version: str) -> int:
        tag = self.get_tag_for_version(version)
        if tag[1] < 1:
            return None

        commit_id = self.get_commit_id_for_tag(tag[0])
        return self.get_commit(commit_id).get_timestamp()

    def get_tags(self):
        try:
            tags = self.execute("git tag")
            return tags
        except subprocess.CalledProcessError as exc:
            logger.error("Git command failed." + str(exc.output), exc_info=True)
            return []

    def get_commit_id_for_tag(self, tag):
        cmd = f"git rev-list -1 {tag}"
        commit_id = ""
        try:
            # TODO: https://stackoverflow.com/questions/16198546/get-exit-code-and-stderr-from-subprocess-call
            commit_id = self.execute(cmd)
            if len(commit_id) > 0:
                return commit_id[0].strip()
        except subprocess.CalledProcessError as e:
            logger.error("Git command failed." + str(e.output), exc_info=True)
            sys.exit(1)

    def get_previous_tag(self, tag):
        # https://git-scm.com/docs/git-describe
        commit = self.get_commit_id_for_tag(tag)
        cmd = f"git describe --abbrev=0 --all --tags --always {commit}^"

        try:
            tags = self.execute(cmd)
            if len(tags) > 0:
                return tags
        except subprocess.CalledProcessError as e:
            logger.error("Git command failed." + str(e.output), exc_info=True)
            return []

    def get_issue_or_pr_text_from_id(self, id):
        """
        Return the text of the issue or PR with the given id
        """
        cmd = f"git fetch origin pull/{id}/head"


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


def make_raw_commit(
    repository: Git,
    id: str,
    timestamp: int,
    parent_id: str = "",
) -> RawCommit:
    return RawCommit(repository, id, parent_id)
