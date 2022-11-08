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

import requests

from git.exec import Exec
from git.raw_commit import RawCommit
from log.logger import logger
from stats.execution import execution_statistics, measure_execution_time
from util.lsh import (
    build_lsh_index,
    compute_minhash,
    encode_minhash,
    get_encoded_minhash,
)

# GIT_CACHE = os.getenv("GIT_CACHE")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GIT_SEPARATOR = "-@-@-@-@-"

FILTERING_EXTENSIONS = ["java", "c", "cpp", "py", "js", "go", "php", "h", "jsp"]
RELEVANT_EXTENSIONS = [
    "java",
    "c",
    "cpp",
    "h",
    "py",
    "js",
    "xml",
    "go",
    "rb",
    "php",
    "sh",
    "scale",
    "lua",
    "m",
    "pl",
    "ts",
    "swift",
    "sql",
    "groovy",
    "erl",
    "swf",
    "vue",
    "bat",
    "s",
    "ejs",
    "yaml",
    "yml",
    "jar",
]

# if not os.path.isdir(GIT_CACHE):
#     raise ValueError(
#         f"Environment variable GIT_CACHE is not set or it points to a directory that does not exist: {GIT_CACHE}"
#     )


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
        # self.lsh_index = build_lsh_index()

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

                self.execute("git fetch --progress --all --tags")
            return

        if os.path.exists(self.path):
            logger.debug(f"Folder {self.path} is not a git repository.")
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

    def get_tags():
        cmd = "git log --tags --format=%H - %D"
        pass

    @measure_execution_time(execution_statistics.sub_collection("core"))
    def create_commits(
        self,
        ancestors_of=None,
        exclude_ancestors_of=None,
        since=None,
        until=None,
        find_in_code="",
        find_in_msg="",
        find_twins=True,
    ) -> Dict[str, RawCommit]:
        cmd = f"git log --name-only --full-index --format=%n{GIT_SEPARATOR}%n%H:%at:%P%n{GIT_SEPARATOR}%n%B%n{GIT_SEPARATOR}%n"

        if ancestors_of is None or find_twins:
            cmd += " --all"

        # by filtering the dates of the tags we can reduce the commit range safely (in theory)
        if ancestors_of:
            if not find_twins:
                cmd += f" {ancestors_of}"
            until = self.extract_tag_timestamp(ancestors_of)
        # TODO: if find twins is true, we dont need the ancestors, only the timestamps
        if exclude_ancestors_of:
            if not find_twins:
                cmd += f" ^{exclude_ancestors_of}"
            since = self.extract_tag_timestamp(exclude_ancestors_of)

        if since:
            cmd += f" --since={since}"

        if until:
            cmd += f" --until={until}"

        # for ext in FILTERING_EXTENSIONS:
        #     cmd += f" *.{ext}"

        try:
            logger.debug(cmd)
            out = self.execute(cmd)
            # if --all is used, we are traversing all branches and therefore we can check for twins

            # TODO: problem -> twins can be merge commits, same commits for different branches, not only security related fixes

            return self.parse_git_output(out, find_twins)

        except Exception:
            logger.error("Git command failed, cannot get commits", exc_info=True)
            return dict()

    # def populate_lsh_index(self, msg: str, id: str):
    #     mh = compute_minhash(msg[:64])
    #     possible_twins = self.lsh_index.query(mh)

    #     self.lsh_index.insert(id, mh)
    #     return encode_minhash(mh), possible_twins

    def parse_git_output(self, raw: List[str], find_twins: bool = False):

        commits: Dict[str, RawCommit] = dict()
        commit = None
        sector = 0
        for line in raw:
            if line == GIT_SEPARATOR:
                if sector == 3:
                    sector = 1
                    if 0 < len(commit.changed_files) < 100:
                        commit.msg = commit.msg.strip()
                        if find_twins:
                            # minhash, twins = self.populate_lsh_index(
                            #     commit.msg, commit.id
                            # )
                            commit.minhash = get_encoded_minhash(commit.msg[:64])
                            # commit.twins = twins
                            # for twin in twins:
                            #     commits[twin].twins.append(commit.id)

                        commits[commit.id] = commit

                else:
                    sector += 1
            else:
                if sector == 1:
                    id, timestamp, parent = line.split(":")
                    parent = parent.split(" ")[0]
                    commit = RawCommit(self, id, int(timestamp), parent)
                elif sector == 2:
                    commit.msg += line + " "
                elif sector == 3 and "test" not in line:
                    commit.add_changed_file(line)

        return commits

    def get_issues(self, since=None) -> Dict[str, str]:
        owner, repo = self.url.split("/")[-2:]
        query_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        # /repos/{owner}/{repo}/issues/{issue_number}
        params = {
            "state": "closed",
            "per_page": 100,
            "since": since,
            "page": 1,
        }
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
        r = requests.get(query_url, params=params, headers=headers)

        while len(r.json()) > 0:
            for elem in r.json():
                body = elem["body"] or ""
                self.issues[str(elem["number"])] = (
                    elem["title"] + " " + " ".join(body.split())
                )

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
            cmd += f" {ancestors_of}"
            until = self.extract_tag_timestamp(ancestors_of)

        if exclude_ancestors_of:
            cmd += f" ^{exclude_ancestors_of}"
            since = self.extract_tag_timestamp(exclude_ancestors_of)

        if since:
            cmd += f" --since={since}"

        if until:
            cmd += f" --until={until}"

        for ext in FILTERING_EXTENSIONS:
            cmd += f" *.{ext}"

        # What is this??
        if find_in_code:
            cmd += f" -S{find_in_code}"

        if find_in_msg:
            cmd += f" --grep={find_in_msg}"

        try:
            logger.debug(cmd)
            out = self.execute(cmd)

        except Exception:
            logger.error("Git command failed, cannot get commits", exc_info=True)
            out = []

        return out

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

    # Return the timestamp for given a version if version exist or None
    def extract_timestamp_from_version(self, version: str) -> int:
        tag = self.get_tag_for_version(version)
        if tag[1] < 1:
            return None

        commit_id = self.get_commit_id_for_tag(tag[0])
        return self.get_commit(commit_id).get_timestamp()

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
