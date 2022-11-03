import os
import subprocess
from functools import lru_cache
from typing import List, Optional

from log.logger import logger


class Exec:
    def __init__(self, workdir=None, encoding="latin-1", timeout=None):
        self.encoding = encoding
        self.timeout = timeout
        self.set_dir(workdir)

    def set_dir(self, path):
        if os.path.isabs(path):
            self._workdir = path
        else:
            raise ValueError(f"Path must be absolute for Exec to work: {path}")

    def run(self, cmd: str, silent=False, cache: bool = False):
        if cache:
            return self.run_cached(cmd, silent)

        return self.run_uncached(cmd, silent)

    # TODO lru_cache only works for one python process.
    # If you are running multiple subprocesses,
    # or running the same script over and over, lru_cache will not work.
    @lru_cache(maxsize=10000)
    def run_cached(self, cmd, silent=False):
        return self.run_uncached(cmd, silent=silent)

    def run_uncached(self, cmd, silent=False):
        if isinstance(cmd, str):
            cmd = cmd.split()

        out = self.execute(cmd, silent=silent)
        if out is None:
            return []
        else:
            return out

    def run_live_output(self, cmd: str):
        if isinstance(cmd, str):
            cmd = cmd.split()
        pass

    def execute(self, cmd, silent=False) -> Optional[List[str]]:
        try:
            out = subprocess.run(
                cmd,
                cwd=self._workdir,
                text=True,
                capture_output=not silent,
                encoding=self.encoding,
            )
            if out.returncode != 0:
                raise Exception(f"{cmd} error: {out.stderr}")

            if silent:
                return None

            return [r for r in out.stdout.split("\n") if r.strip() != ""]
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout exceeded ({self.timeout} seconds)", exc_info=True)
            raise Exception(f"Process did not respond for {self.timeout} seconds")
