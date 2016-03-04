import os
import glob
import tempfile
import shutil
import traceback
import smtplib
from email.mime.text import MIMEText


class TemporaryDirectory(object):
    """
    This class rprovides a context where it is available a temporary
    directory that can be used as a working directory for a task or
    a group of tasks.
    """
    def __init__(self, preserve=False, prefix=''):
        self.tmp_dir = None
        self.preserve = preserve
        self.prefix = prefix

    def __enter__(self):
        if self.preserve:
            self.tmp_dir = self.__get_existing()
        else:
            self.tmp_dir = self.__create_new()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None and self.tmp_dir is not None:
            if not self.preserve:
                shutil.rmtree(self.tmp_dir)

    def __get_existing(self):
        base_tmp = '/tmp'
        tmp_contents = glob.glob(os.path.join(base_tmp, 'ecflow-{}*'.format(self.prefix)))
        if len(tmp_contents) > 1:
            tmp_contents_mtimes = [
                (path, os.stat(path).st_mtime) for path in tmp_contents
            ]
            return max(tmp_contents_mtimes, key=lambda x: x[1])
        elif len(tmp_contents) > 0:
            return tmp_contents[0]
        else:
            return self.__create_new()

    def __create_new(self):
        return tempfile.mkdtemp(prefix='ecflow-{}'.format(self.prefix))

    def clean(self):
        self.preserve = False

    @property
    def path(self):
        return self.tmp_dir


class EmailNotifier(object):
    def __init__(self, server, port, username, password):
        self.__server = server
        self.__port = port
        self.__username = username
        self.__password = password

    def send_email(self, sender, dest, subject, msg):
        s = smtplib.SMTP(self.__server, self.__port)
        s.starttls()
        s.login(self.__username, self.__password)

        msg = MIMEText(msg)
        msg['From'] = sender
        msg['To'] = dest
        msg['Subject'] = subject

        s.sendmail(sender, dest, msg.as_string())
        s.quit()
