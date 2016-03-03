import os
import logging
import subprocess
import shlex

from ecflowrun.context.manager import EcflowContextManager
from ecflowrun.utils import TemporaryDirectory
from ecflowrun.errors import EcflowrunError


class BashTask(object):
    def __init__(self, bash_cmd, env):
        self.__bash_cmd = bash_cmd
        self.__env = env

    def execute(self):
        with EcflowContextManager(**self.__env) as ctx:
            ctx.log(
                'Running bash task with command {}'.format(self.__bash_cmd),
                logging.INFO
            )
            with TemporaryDirectory() as tmp:
                tmp_file_path = os.path.join(tmp.path, 'temporary_script')
                fp = open(tmp_file_path, 'w')
                fp.write(self.__bash_cmd)
                fp.flush()
                sp = subprocess.Popen(
                    shlex.split('/bin/bash {}'.format(tmp_file_path)),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                out, err = sp.communicate()
                retcode = sp.returncode
                if retcode:
                    raise EcflowrunError(
                        'Failed to execute BashTask with command {}'.format(self.__bash_cmd)
                    )
