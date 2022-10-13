import os
import subprocess
from functools import lru_cache

import log.util

_logger = log.util.init_local_logger()


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

    def run(self, cmd, ignore_output=False, cache: bool = False):
        if cache:
            result = self._run_cached(
                tuple(cmd) if isinstance(cmd, list) else cmd, ignore_output
            )
        else:
            result = self._run_uncached(
                tuple(cmd) if isinstance(cmd, list) else cmd, ignore_output
            )
        return result

    @lru_cache(maxsize=10000)
    def _run_cached(self, cmd, ignore_output=False):
        return self._run_uncached(cmd, ignore_output=ignore_output)

    def _run_uncached(self, cmd, ignore_output=False):
        if isinstance(cmd, str):
            cmd = cmd.split()

        if ignore_output:
            self._execute_no_output(cmd)
            return ()

        result = self._execute(cmd)
        if result is None:
            return ()

        return tuple(result)

    def _execute_no_output(self, cmd_l):
        try:
            subprocess.check_call(
                cmd_l,
                cwd=self._workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:  # pragma: no cover
            _logger.error(
                "Timeout exceeded (" + self._timeout + " seconds)", exc_info=True
            )
            raise Exception("Process did not respond for " + self._timeout + " seconds")

    def _execute(self, cmd_l):
        try:
            proc = subprocess.Popen(
                cmd_l,
                cwd=self._workdir,
                stdout=subprocess.PIPE,
                # stderr=subprocess.STDOUT,  # Needed to have properly prinded error output
            )
            out, _ = proc.communicate()

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
            _logger.error(f"Timeout exceeded ({self._timeout} seconds)", exc_info=True)
            raise Exception(f"Process did not respond for {self._timeout} seconds")
            # return None
        # except Exception as ex:                 # pragma: no cover
        #     traceback.print_exc()
        #     raise ex
