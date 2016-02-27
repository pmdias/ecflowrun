"""
Administration utilities for Ecflow.
"""
from ecflow import ecflow

import os
import argparse
import subprocess
import shlex


def ecflow_admin():
    """
    Function that manages the arguments provided through the console and
    that performs the required administrative work.
    """
    parser = _build_cmd_parser()
    args = parser.parse_args()
    action = args.action
    host = args.host
    port = args.port
    home = args.home

    if action == 'status':
        _ping_server(host, port)
    elif action == 'start':
        _start_server(host, port, home)
    elif action == 'stop':
        _stop_server(host, port)


def _build_cmd_parser():
    parser = argparse.ArgumentParser(
        description='Administrative command line tool for Ecflow server'
    )
    parser.add_argument(
        '-H',
        '--host',
        help='Server host',
        default='localhost'
    )
    parser.add_argument(
        '-p',
        '--port',
        help='Server port',
        default=3141
    )
    parser.add_argument(
        '-d',
        '--home',
        help='Home directory to run the server',
        default=os.path.join(os.getenv('HOME'), '.ecflow_server')
    )
    parser.add_argument(
        'action',
        choices=[
            'start',
            'stop',
            'status'
        ],
        help='Task to be performed'
    )

    return parser


def _start_server(host, port, home):
    pass


def _ping_server(host, port):
    """
    Uses an instance of ecflow.Client to ping the target server. Returns
    true if the server replies correctly and false otherwise.
    """
    try:
        cl = ecflow.Client(host, port)
        cl.ping()
    except RuntimeError as e:
        print 'Server is not running'
        return False
    else:
        print 'Server is up and running'
        return True


def _stop_server(port):
    """
    Stop a local ecflow server service.
    """
    cmd = 'ecflow_client --host={host} --port={port}'.format(host='localhost', port=port)
