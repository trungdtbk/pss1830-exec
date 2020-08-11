#!/usr/bin/env python

from __future__ import print_function
import sys
import time
import re
import argparse
from datetime import datetime

from psscli import PSSCli
from pssroot import PSSRoot
from __version__ import VERSION

def err(msg):
    pass

def out(msg):
    print(msg, end='')

def get_parser():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="1830PSS Executor")
    parser.add_argument('-m', '--mode', type=str, choices=['root', 'cli'], required=True,
                        help="Mode for commands: can be either as root or cli")
    parser.add_argument('--host', type=str, help="IP address of PSS node", required=True)
    parser.add_argument('--port', help="Port (default: 22)", default=22, type=int)
    parser.add_argument('-u', '--user', required=True, help="Username", type=str)
    parser.add_argument('-p', '--pass', metavar="p", required=True, help="Password", type=str)
    parser.add_argument('-c', '--command', required=True, nargs="+", 
                        help="Command(s). Can be repeated", action="append", type=str)
    parser.add_argument('-w', '--timeout',
                        help="Timeout (s) for sending/waiting for commands/results", type=int)
    parser.add_argument('-v', '--version', action="version", version=VERSION)

    return parser

def get_config(args):
    config = {}
    config['mode'] = args.mode
    config['host'] = args.host
    config["port"] = args.port
    config["commands"] = [cmd for group in args.command for cmd in group]
    config["username"] = args.user
    config["password"] = vars(args)['pass']
    config['timeout'] = args.timeout
    return config

def run(config):
    out('Start execution: %s\n' % datetime.now())
    if config['mode'] == 'root':
        PSS = PSSRoot
    else:
        PSS = PSSCli
    pss = PSS(config['host'], config['port'], config['username'], config['password'])
    if config['timeout']:
        pss.TIMEOUT = config['timeout']
    pss.open()
    if not (pss.connected and pss.prompt):
        pss.close()
        out('\nFailed to login to the node\n')
        sys.exit(-1)
    
    for command in config['commands']:
        try:
            out('\nExecuting command: %s\n' % command)
            for data in pss.execute(command):
                out(data)
        except Exception as e:
            out('Error during executing command (%s): %s\n' % (command, e))
        time.sleep(0.0)
    pss.close()
    out('\nFinished: %s\n' % datetime.now())

def main():
    parser = get_parser()
    args = parser.parse_args()
    config = get_config(args)
    run(config)

if __name__ == '__main__':
    main()
