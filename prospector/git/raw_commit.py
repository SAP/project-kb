import sys

import hashlib
import re
from datetime import timezone
from dateutil.parser import isoparse
import log.util
from git.exec import Exec
from stats.execution import execution_statistics, measure_execution_time


_logger = log.util.init_local_logger()


class RawCommit:
    def __init__(
        self, repository_url: str, commit_id: str, exec_link: Exec, init_data=None
    ):
        self.repository_url = repository_url
        self.id = commit_id
        self.exec = exec_link
        self.timestamp = self.extract_timestamp()
        self.parent_id = self.extract_parent_id()

    def execute(self, cmd):
        return self.exec.run(cmd, cache=True)

    def get_id(self) -> str:
        return self.id

    def extract_parent_id(self):
        try:
            cmd = f"git log --format=%P -1 {self.id}"
            parent = self.execute(cmd)
            if len(parent) > 0:
                return parent[0]
        except:
            _logger.error(
                f"Failed to obtain parent id for: {self.id}",
                exc_info=True,
            )
        return ""

    def get_timestamp(self):
        return self.timestamp

    def get_parent_id(self):
        return self.parent_id

    def get_repository_url(self):
        return self.repository_url

    def get_msg(self):
        try:
            cmd = f"git log --format=%B -1 {self.id}"
            return " ".join(self.execute(cmd))
        except Exception:
            _logger.error(
                f"Failed to obtain commit message for commit: {self.id}",
                exc_info=True,
            )
            return ""

    def get_diff(self, context_size: int = 1, filter_files: str = ""):
        if self.parent_id == "":
            return ""
        try:
            cmd = f"git diff --unified={context_size} {self.id}^!"

            if filter_files:
                cmd += f" *.{filter_files}"

            return self.execute(cmd)

        except Exception:
            _logger.error(
                f"Failed to obtain patch for commit: {self.id}",
                exc_info=True,
            )
            return ""

    def extract_timestamp(self, format_date=False):
        try:
            if not format_date:
                cmd = f"git log --format=%at -1 {self.id}"
                return int(self.execute(cmd)[0])
            else:
                cmd = f"git log --format=%aI -1 {self.id}"
                return (
                    isoparse(self.execute(cmd)[0])
                    .astimezone(timezone.utc)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )

        except Exception as e:
            _logger.error(
                f"Failed to obtain timestamp for commit: {self.id}",
                exc_info=True,
            )
            raise Exception("Failed to obtain timestamp for commit: " + self.id)

    @measure_execution_time(
        execution_statistics.sub_collection("core"),
        name="retrieve changed file from git",
    )
    def get_changed_files(self):
        if self.parent_id == "":
            return []

        try:
            cmd = f"git diff --name-only {self.id}^!"
            return self.execute(cmd)  # This is a tuple
        # This exception is raised when the commit is the first commit in the repository
        except Exception:
            _logger.error(
                f"Failed to obtain changed files for commit {self.id}, it may be the first commit of the repository. Processing anyway...",
                exc_info=True,
            )
            return []

    def get_changed_paths(self, other: "RawCommit" = None, match=None):
        # TODO refactor, this overlaps with changed_files
        # Maybe useless
        if other is None:
            other_id = self.id + "^"
        else:
            other_id = other.id

        try:
            cmd = f"git log --name-only --format=%n --full-index {other_id}..{self.id}"

            out = self.execute(cmd)
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write(
                f"Problem retriving the list of commits in the interval {other.id}..{self.id}\n"
            )
            return ""

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

        hunks = []

        diff_lines = self.get_diff()

        first_line_of_current_hunk = -1
        current_group = []
        line_no = 0
        for line_no, line in enumerate(diff_lines):
            # print(line_no, " : ", line)
            if is_new_file(line):
                if len(current_group) > 0:
                    hunks.append(current_group)
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

        hunks.append(current_group)

        if grouped:
            return hunks
        else:
            return flatten_groups(hunks)

    # def __eq__(self, other: "RawCommit") -> bool:
    #     return self.get_fingerprint == other.get_fingerprint()

    def equals(self, other: "RawCommit"):
        """
        Return true if the two commits contain the same changes (despite different commit messages)
        """
        return self.get_fingerprint() == other.get_fingerprint()

    def get_fingerprint(self):
        cmd = f"git show --format=%t --numstat {self.id}"
        out = self.execute(cmd)
        return hashlib.md5("\n".join(out).encode()).hexdigest()

    def get_timing_data(self):
        data = self._get_timing_data()

        return {
            "next_tag": data[0],
            "next_tag_timestamp": data[1],
            "timestamp": data[2],
            "time_to_tag": data[3],
        }

    # TODO: deprecated / unused stuff
    def _get_timing_data(self):

        # get tag info
        tags = self.execute(f"git tag --sort=taggerdate --contains {self.id}")

        tag = ""
        tag_timestamp = "0"

        if len(tags) > 0:
            tag = tags[0]
            tag_timestamp = self.execute(f"git show -s --format=%at {tag}^{self.id}")[
                0
            ][1:-1]

        try:
            commit_timestamp = self.execute(f"git show -s --format=%at {self.id}")[0][
                1:-1
            ]
            time_delta = int(tag_timestamp) - int(commit_timestamp)
            if time_delta < 0:
                time_delta = -1
        except:
            commit_timestamp = "0"
            time_delta = 0

        self._timestamp = commit_timestamp
        return (tag, tag_timestamp, commit_timestamp, time_delta)

    def get_tags(self):
        cmd = f"git tag --contains {self.id}"
        tags = self.execute(cmd)
        if not tags:
            return []
        return tags

    def get_next_tag(self):
        data = self.get_timing_data()
        return (
            data.get("next_tag"),
            data.get("next_tag_timestamp"),
            data.get("time_to_tag"),
        )

    def __str__(self):
        data = (
            self.id,
            self.get_timestamp(date_format="%Y-%m-%d %H:%M:%S"),
            self.get_timestamp(),
            self.repository_url,
            self.get_msg(),
            len(self.get_hunks()),
            len(self.get_changed_paths()),
            self.get_next_tag()[0],
            "\n".join(self.get_changed_paths()),
        )
        return """
        Commit id:         {}
        Date (timestamp):  {} ({})
        Repository:        {}
        Message:           {}
        hunks: {},  changed files: {},  (oldest) tag: {}
        {}""".format(
            *data
        )


# class RawCommitSet:
#     def __init__(self, repo=None, commit_ids=[], prefetch=False):

#         if repo is not None:
#             self.repository = repo
#         else:
#             raise ValueError  # pragma: no cover

#         self._commits = []

#         # TODO when the flag 'prefetch' is True, fetch all data in one shot (one single
#         # call to the git binary) and populate all commit objects. A dictionary paramenter
#         # passed to the Commit constructor will be used to pass the fields that need to be populated
#         commits_count = len(commit_ids)
#         if prefetch is True and commits_count > 50:
#             _logger.warning(
#                 f"Processing {commits_count:d} commits will take some time!"
#             )
#             for cid in commit_ids:
#                 commit_data = {"id": "", "msg": "", "patch": "", "timestamp": ""}
#                 current_field = None
#                 commit_raw_data = self.repository._exec.run(
#                     "git show --format=@@@@@SHA1@@@@@%n%H%n@@@@@LOGMSG@@@@@%n%s%n%b%n@@@@@TIMESTAMP@@@@@@%n%at%n@@@@@PATCH@@@@@ "
#                     + cid,
#                     cache=True,
#                 )

#                 for line in commit_raw_data:
#                     if line == "@@@@@SHA1@@@@@":
#                         current_field = "id"
#                     elif line == "@@@@@LOGMSG@@@@@":
#                         current_field = "msg"
#                     elif line == "@@@@@TIMESTAMP@@@@@":
#                         current_field = "timestamp"
#                     else:
#                         commit_data[current_field] += "\n" + line

#                 self._commits.append(
#                     RawCommit(self.repository, cid, init_data=commit_data)
#                 )
#         else:
#             self._commits = [RawCommit(self.repository, c) for c in commit_ids]

#     def get_all(self):
#         return self._commits

#     def add(self, commit_id):
#         self._commits.append(RawCommit(self.repository, commit_id))
#         return self

#     def filter_by_msg(self, word):
#         return [c for c in self.get_all() if word in c.get_msg()]
