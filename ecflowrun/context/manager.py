import os
import subprocess
import traceback
import shlex
import signal
import logging

from ecflowrun.errors import EcflowrunError


logging.basicConfig(format='[%(asctime)s] %(message)s')


class EcflowContextManager(object):
    """
    Context manager that creates and manages a new context allowing
    to run an Ecflow job. The manager initializes the job in the
    Ecflow server and setups all the required logic to handle both
    success and failure of the job. It also registers the required
    signal handlers.

    On initialization, several Ecflow variables must be passed to
    the manager so that it updates the process environment. The
    mandatory variables are:
    * ECF_NAME
    * ECF_PASS
    * ECF_NODE
    * ECF_PORT
    * ECF_TRYNO

    Also, the manager automatically setups the variable ECF_RID to
    the current PID.
    """

    # List of signals that are trapped and handled by the
    # EcflowContextManager
    _TRAPPED_SIGNALS = [
        signal.SIGHUP,
        signal.SIGINT,
        signal.SIGQUIT,
        signal.SIGILL,
        signal.SIGTRAP,
        signal.SIGABRT,
        signal.SIGBUS,
        signal.SIGFPE,
        signal.SIGUSR1,
        signal.SIGUSR2,
        signal.SIGPIPE,
        signal.SIGTERM
    ]

    # List of mandatory Ecflow variables that must be passed as argument
    # to the init of the EcflowContextManager
    _MANDATORY_VARS = set([
        'ECF_NAME',
        'ECF_PASS',
        'ECF_NODE',
        'ECF_PORT',
        'ECF_TRYNO'
    ])

    def __init__(self, **kwargs):
        if not self._MANDATORY_VARS.issubset(set(kwargs.keys())):
            raise EcflowrunError

        self.__env = {}
        for k, v in kwargs.iteritems():
            self.__env[k] = v
        self.__env['ECF_RID'] = str(os.getpid())
        os.environ.update(self.__env)
        self.__register_signals()

        # Setup a basic logger
        self.logger = logging.getLogger(kwargs.pop('LOGGER'))
        self.logger.setLevel(logging.INFO)

    def __enter__(self):
        """
        As we enter the managed context, we signal the Ecflow server
        that the job as started.
        """
        self.__job_init()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """
        As we exit the managed context, we evaluate if there was any error
        and proceed to signal the Ecflow server with a job abort if any
        error was detected. Otherwise, we just signal that the job as
        completed.
        """
        if exc_type:
            print traceback.format_exception(exc_type, exc_value, exc_tb)
            self.__job_abort()
            return False
        self.__job_complete()
        return True

    def __run_cmd(self, cmd):
        """
        Generic way of sending commands to the ecflow_client. Probably
        best to investigate if this can be done using the ecflow.Client
        instead of an indirect call through a child process.
        """
        raw_cmd = 'ecflow_client --{}'.format(cmd)
        splitted = shlex.split(raw_cmd)
        process = subprocess.Popen(
            splitted,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        retcode = process.returncode
        return out, err, retcode

    def __job_init(self):
        """
        Signal the Ecflow server that the job as started.
        """
        out, err, retcode = self.__run_cmd(
            'init={}'.format(self.__env['ECF_RID'])
        )
        if retcode:
            raise EcflowrunError(
                'Initialization failed with return code {}'.format(retcode)
            )

    def __job_complete(self):
        """
        Signal the Ecflow server that the job is complete.
        """
        out, err, retcode = self.__run_cmd('complete')
        if retcode:
            raise EcflowrunError(
                'Complete failed with return code {}'.format(retcode)
            )

    def __job_abort(self):
        """
        Signal the Ecflow server that the job was aborted.
        """
        out, err, retcode = self.__run_cmd(
            'abort={}'.format(self.__env['ECF_RID'])
        )
        if retcode:
            raise EcflowrunError(
                'Abort failed with return code {}'.format(retcode)
            )

    def __signal_handler(self, signum, stframe):
        """
        Abort the job if the process is signalled with the
        signal number being registered.
        """
        self.__job_abort()

    def __register_signals(self):
        """
        Register the generic signal handler for all signals
        that we can catch.
        """
        for s in self._TRAPPED_SIGNALS:
            signal.signal(s, self.__signal_handler)

    def log(self, msg, lvl):
        """
        Log a message with the corresponding level.
        """
        self.logger.log(lvl, msg)

    def force_abort(self):
        """
        Allows a job to abort itself.
        """
        return self.__job_abort()

    def event(self, ev):
        """
        Use the ecflow client to launch an Ecflow event.
        """
        out, err, retcode = self.__run_cmd('event={}'.format(ev))
        if retcode:
            raise EcflowrunError(
                'Failed to raise event with return code {}'.format(retcode)
            )

    def label(self, name, msg):
        """
        Update the message of an Ecflow node label, identified by its
        name.
        """
        out, err, retcode = self.__run_cmd('label={0} "{1}"'.format(name, msg))
        if retcode:
            raise EcflowrunError(
                'Failed to set label message with return code {}'.format(retcode)
            )

    def meter(self, name, val):
        """
        Update the value of an Ecflow meter, identifier by its name.
        """
        out, err, retcode = self.__run_cmd('meter={0} {1}'.format(name, val))
        if retcode:
            raise EcflowrunError(
                'Failed to update meter value with return code {}'.format(retcode)
            )
