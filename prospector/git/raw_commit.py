import hashlib
from datetime import timezone
from typing import List, Tuple

from dateutil.parser import isoparse

from log.logger import logger


# Removed type hints for repository to avoid circular import
class RawCommit:
    def __init__(
        self,
        repository,
        commit_id: str = "",
        timestamp: int = 0,
        parent_id: str = "",
        msg: str = "",
        minhash: str = "",
        changed_files: List[str] = None,
        twins: List[str] = None,
    ):
        self.repository = repository
        self.id = commit_id
        self.timestamp = timestamp
        self.parent_id = parent_id
        self.msg = msg
        self.minhash = minhash
        self.twins = []
        self.changed_files = []

    def __str__(self) -> str:
        return f"ID:  {self.id}\nURL: {self.get_repository_url()}\nTS:  {self.timestamp}\nPID: {self.parent_id}\nCF:  {self.changed_files}\nMSG: {self.msg}"

    def execute(self, cmd):
        return self.repository.execute(cmd)

    def get_repository_url(self) -> str:
        return self.repository.url

    def get_id(self) -> str:
        return self.id

    def get_minhash(self) -> str:
        return self.minhash

    def set_changed_files(self, changed_files: List[str]):
        self.changed_files = changed_files

    def add_changed_file(self, changed_file: str):
        self.changed_files.append(changed_file)

    def get_twins(self):
        return self.twins

    def set_tags(self, tags: List[str]):
        self.tags = tags

    # def extract_parent_id(self):
    #     try:
    #         cmd = f"git log --format=%P -1 {self.id}"
    #         parent = self.execute(cmd)
    #         if len(parent) > 0:
    #             self.parent_id = parent[0]
    #         else:
    #             self.parent_id = ""
    #     except Exception:
    #         logger.error(
    #             f"Failed to obtain parent id for: {self.id}",
    #             exc_info=True,
    #         )
    #         self.parent_id = ""

    def get_timestamp(self):
        return self.timestamp

    def get_parent_id(self):
        return self.parent_id

    def get_msg(self):
        return self.msg.strip()

    def get_msg_(self):
        try:
            cmd = f"git log --format=%B -1 {self.id}"
            msg = self.execute(cmd)
            # When we retrieve the commit message we compute the minhash and we add it to the repository index
            # self.repository.add_to_lsh(compute_minhash(msg[0]))
            return " ".join(msg)
        except Exception:
            logger.error(
                f"Failed to obtain commit message for commit: {self.id}",
                exc_info=True,
            )
            return ""

    # def extract_gh_references(self):
    #     """
    #     Extract the GitHub references from the commit message
    #     """
    #     gh_references = dict()
    #     for result in re.finditer(r"(?:#|gh-)(\d+)", self.msg):
    #         id = result.group(1)
    #         if id in self.repository.issues:
    #             gh_references[id] = self.repository.issues[id]
    #     return gh_references

    def get_hunks_count(self, diffs: List[str]):
        hunks_count = 0
        flag = False
        for line in diffs:
            if line[:3] in ("+++", "---"):
                continue
            if line[:1] in "-+" and not flag:
                hunks_count += 1
                flag = True
            elif line[:1] in "-+" and flag:
                continue

            if line[:1] not in "-+":
                flag = False
        return hunks_count

    def get_diff(self) -> Tuple[List[str], int]:
        """Return an array containing the diff lines, and the hunks count"""
        if self.parent_id == "":
            return "", 0
        try:
            cmd = f"git diff --unified=1 {self.id}^!"
            diffs = self.execute(cmd)
            return diffs, self.get_hunks_count(diffs)

        except Exception:
            logger.error(
                f"Failed to obtain patch for commit: {self.id}",
                exc_info=True,
            )
            return "", 0

    def extract_timestamp(self, format_date=False):
        try:
            if not format_date:
                cmd = f"git log --format=%at -1 {self.id}"
                self.timestamp = int(self.execute(cmd)[0])
            else:
                cmd = f"git log --format=%aI -1 {self.id}"
                self.timestamp = (
                    isoparse(self.execute(cmd)[0])
                    .astimezone(timezone.utc)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )

        except Exception:
            logger.error(
                f"Failed to obtain timestamp for commit: {self.id}",
                exc_info=True,
            )
            raise Exception(f"Failed to obtain timestamp for commit: {self.id}")

    # @measure_execution_time(
    #     execution_statistics.sub_collection("core"),
    #     name="retrieve changed file from git",
    # )
    # def get_changed_files_(self):
    #     if self.parent_id == "":
    #         return []
    #     # TODO: if only contains test classes remove from list
    #     try:
    #         cmd = f"git diff --name-only {self.id}^!"
    #         files = self.execute(cmd)
    #         for file in files:
    #             if "test" not in file:
    #                 return files
    #         return []
    #     # This exception is raised when the commit is the first commit in the repository
    #     except Exception:
    #         logger.error(
    #             f"Failed to obtain changed files for commit {self.id}, it may be the first commit of the repository. Processing anyway...",
    #             exc_info=True,
    #         )
    #         return []

    def get_changed_files(self):
        return self.changed_files

    def validate_changed_files(self) -> bool:
        """If the changed files are only test classes, return False"""
        return any("test" not in file for file in self.changed_files)

    # TODO: simplify this method
    def get_hunks_old(self, grouped=False):  # noqa: C901
        def is_hunk_line(line):
            return line[0] in "-+" and (len(line) < 2 or (line[1] != line[0]))

        def flatten_groups(hunk_groups):
            hunks = []
            for group in hunk_groups:
                for h in group:
                    hunks.append(h)
            return hunks

        def is_new_file(cmd):
            return cmd[0:11] == "diff --git "

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
        except Exception:
            commit_timestamp = "0"
            time_delta = 0

        self._timestamp = commit_timestamp
        return (tag, tag_timestamp, commit_timestamp, time_delta)

    def get_tags(self):
        cmd = f"git tag --contains {self.id}"
        # cmd = f"git log --format=oneline"  # --date=unix --decorate=short"
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
