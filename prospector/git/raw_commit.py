from datetime import timezone
from typing import List, Optional, Tuple

from dateutil.parser import isoparse

from log.logger import logger


class RawCommit:
    def __init__(
        self,
        repository,
        commit_id: str = "",
        tags: List[str] = None,
        timestamp: int = 0,
        parent_id: str = "",
        msg: str = "",
        changed_files: List[str] = None,
    ):
        self.repository = repository
        self.id = commit_id
        self.timestamp = timestamp
        self.parent_id = parent_id
        self.msg = msg
        self.changed_files = changed_files or []

    def __str__(self) -> str:
        return f"ID:  {self.id}\nURL: {self.get_repository_url()}\nTS:  {self.timestamp}\nPID: {self.parent_id}\nCF:  {self.changed_files}\nMSG: {self.msg}\nTAG: {self.tags}"

    def execute(self, cmd):
        return self.repository.execute(cmd)

    def get_repository_url(self) -> str:
        return self.repository.url

    def get_id(self) -> str:
        return self.id

    def set_changed_files(self, changed_files: List[str]):
        self.changed_files = changed_files

    def add_changed_file(self, changed_file: str):
        self.changed_files.append(changed_file)

    def find_tags(self):
        return self.execute(f"git tag --contains {self.id}")

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_parent_id(self):
        return self.parent_id

    def get_msg(self, limit_length: Optional[int] = None) -> str:
        return self.msg[:limit_length] if limit_length else self.msg

    def get_hunks_count(self, diffs: List[str]):
        hunks_count = 0
        flag = False
        for line in diffs:
            if line[:3] in ("+++", "---"):
                continue
            if line[0] in "-+" and not flag:
                hunks_count += 1
                flag = True
            elif line[0] in "-+" and flag:
                continue

            if line[0] not in "-+":
                flag = False
        return hunks_count

    def get_diff(self) -> Tuple[List[str], int]:
        """Return an array containing the diff lines, and the hunks count"""
        if self.parent_id == "":
            return "", 0
        try:
            # We already filtered out in Git the "useless files, so we can exclude them from the diff also. Reduces false positives rules."
            cmd = f"git diff --unified=1 {self.id}^! -- " + " ".join(self.changed_files)
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

    def exists(self):
        try:
            self.execute(f"git log -1 {self.id}")
            return True
        except Exception:
            return False

    def get_changed_files(self):
        return self.changed_files
