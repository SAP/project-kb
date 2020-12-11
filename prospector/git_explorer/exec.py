# from .utils import execute_l
import subprocess
# import logging
import traceback
import os


class Exec:
    def __init__(self, workdir=None, encoding="latin-1", timeout=None):
        self._encoding = encoding
        self._timeout = timeout
        self.setDir(workdir)

    def setDir(self, path):
        if os.path.isabs(path):
            self._workdir = path
        else:
            raise ValueError('Path must be absolute for Exec to work: ' + path)

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
            subprocess.check_call(cmd_l,
                                    cwd=self._workdir,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired: # pragma: no cover
            print('Timeout exceeded (' + self._timeout + ' seconds)')
            raise Exception('Process did not respond for ' + self._timeout + ' seconds')

    def _execute(self, cmd_l):
        try:
            proc = subprocess.Popen(cmd_l, cwd=self._workdir, stdout=subprocess.PIPE)
            out, err = proc.communicate()

            if proc.returncode != 0:
                raise Exception("Process (%s) exited with non-zero return code" % ' '.join(cmd_l))
            # if err:       # pragma: no cover
            #     traceback.print_exc()
            #     raise Exception('Execution failed')

            raw_output_list = out.decode(self._encoding).split('\n')
            return [r for r in raw_output_list if r.strip() != '']
        except subprocess.TimeoutExpired: # pragma: no cover
            print('Timeout exceeded (' + self._timeout + ' seconds)')
            raise Exception('Process did not respond for ' + self._timeout + ' seconds')
            # return None
        # except Exception as ex:                 # pragma: no cover
        #     traceback.print_exc()
        #     raise ex
