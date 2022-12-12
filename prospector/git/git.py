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

GIT_SEPARATOR = "-@-@-@-@-"

TEN_DAYS_TIME_DELTA = 14 * 24 * 60 * 60
ONE_MONTH_TIME_DELTA = 30 * 24 * 60 * 60


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


class Git:
    def __init__(
        self,
        url: str,
        cache_path=os.path.abspath("/tmp/gitcache"),
        shallow: bool = False,
    ):
        pathlib.Path(cache_path).mkdir(parents=True, exist_ok=True)
        self.repository_type = "GIT"
        self.url = url
        self.path = path_from_url(url, cache_path)
        self.fingerprints = dict()
        self.exec_timeout = None
        self.shallow_clone = shallow
        self.exec = Exec(workdir=self.path)
        self.storage = None

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
        if shallow is not None:
            self.shallow_clone = shallow

        if not self.url:
            raise Exception("Invalid or missing url.")

        # TODO rearrange order of checks
        if os.path.isdir(os.path.join(self.path, ".git")):
            if skip_existing:
                logger.debug(f"Skipping fetch of {self.url} in {self.path}")
            else:
                logger.debug(f"Found repo {self.url} in {self.path}.\nFetching....")

                self.execute("git fetch --progress --all --tags --force")
            return

        if os.path.exists(self.path):
            logger.info(f"Folder {self.path} is not a git repository.")
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
        except Exception as e:
            logger.error(f"Could not update remote in {self.path}", exc_info=True)
            shutil.rmtree(self.path)
            raise e

        try:
            if self.shallow_clone:
                self.execute("git fetch --depth 1")
            else:
                self.execute("git fetch --progress --all --tags")
        except Exception as e:
            logger.error(
                f"Could not fetch {self.url} (shallow={self.shallow_clone}) in {self.path}",
                exc_info=True,
            )
            shutil.rmtree(self.path)
            raise e

    @measure_execution_time(execution_statistics.sub_collection("core"))
    def create_commits(
        self,
        next_tag=None,
        prev_tag=None,
        since=None,
        until=None,
        filter_extension=None,
        find_in_code="",
        find_in_msg="",
    ) -> Dict[str, RawCommit]:
        cmd = f"git log --all --name-only --full-index --format=%n{GIT_SEPARATOR}%n%H:%at:%P%n{GIT_SEPARATOR}%n%B%n{GIT_SEPARATOR}%n"

        if next_tag:
            until = self.extract_tag_timestamp(next_tag) + TEN_DAYS_TIME_DELTA
        if until:
            cmd += f" --until={until}"

        # TODO: if find twins is true, we dont need the ancestors, only the timestamps
        if prev_tag:
            since = self.extract_tag_timestamp(prev_tag) - TEN_DAYS_TIME_DELTA
        if since:
            cmd += f" --since={since}"

        if filter_extension:
            cmd += " *." + " *.".join(filter_extension)

        try:
            logger.debug(cmd)
            out = self.execute(cmd)
            return self.parse_git_output(out)

        except Exception:
            logger.error("Git command failed, cannot get commits", exc_info=True)
            return dict()

    def parse_git_output(self, raw: List[str]) -> Dict[str, RawCommit]:
        commits: Dict[str, RawCommit] = dict()
        commit = None
        sector = 0
        raw.append(GIT_SEPARATOR)
        for line in raw:
            if line == GIT_SEPARATOR:
                if sector == 3:
                    sector = 1
                    commit.msg = commit.msg.strip()
                    commits[commit.id] = commit
                else:
                    sector += 1
            else:
                if sector == 1:
                    id, timestamp, parent = line.split(":")
                    commit = RawCommit(
                        repository=self,
                        commit_id=id,
                        timestamp=int(timestamp),
                        parent_id=parent.split()[0] if len(parent) else "",
                    )
                elif sector == 2:
                    commit.msg += line + " "
                elif sector == 3:
                    commit.changed_files.append(line)

        return commits

    def find_commits_for_twin_lookups(self, commit_id):
        commit_timestamp = self.extract_tag_timestamp(commit_id)
        return self.create_commits(
            since=commit_timestamp - ONE_MONTH_TIME_DELTA,
            until=commit_timestamp + ONE_MONTH_TIME_DELTA,
        )

    @measure_execution_time(execution_statistics.sub_collection("core"))
    def get_commit(self, id):
        return RawCommit(self, id)

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

    def get_tags(self):
        try:
            return self.execute("git tag")
        except subprocess.CalledProcessError as exc:
            logger.error("Git command failed." + str(exc.output), exc_info=True)
            return []

    def get_commit_id_for_tag(self, tag):
        cmd = f"git rev-list -1 {tag}"
        commit_id = ""
        try:
            commit_id = self.execute(cmd)
            if len(commit_id) > 0:
                return commit_id[0].strip()
        except subprocess.CalledProcessError as e:
            logger.error("Git command failed." + str(e.output), exc_info=True)
            sys.exit(1)


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
    parent_id: str = "",
) -> RawCommit:
    return RawCommit(repository, id, parent_id)
