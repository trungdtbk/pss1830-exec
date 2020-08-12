#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import paramiko
import time
import sys
import os

from pssroot import PSSRoot

def get_parser():
    parser = argparse.ArgumentParser(description="1830PSS debugdump collector")
    parser.add_argument('--host', required=True, help="NE IP address", type=str)
    parser.add_argument('--port', default=5122, help="Port. Default: 5122", type=int)
    parser.add_argument('-u', '--user', help="Login user. Default: root", default="root", type=str)
    parser.add_argument('-p', '--pass', help="Root password", required=True)
    parser.add_argument('-d', '--dest', help="Destination directory. Default: current dir", default='.')
    parser.add_argument('-a', '--all', help="Collect all dumps using all_dump", action="store_true")
    parser.add_argument('-w', '--timeout', help="Timeout to wait for result (default: 30 secs)", default=30, type=int)
    return parser

def get_config(args):
    config = vars(args)    
    return config

def progress(size, sent):
    sys.stdout.write("Transfered: %.2f%%   \r" % (float(sent)/float(size)*100))

def execute(pss, command):
    for line in pss.execute(command):
        print(line, end="")
    print("\n")

def collect_debug_dump(pss, dest):

    def create_debug_dump(pss):
        print('Creating debug_dump')
        execute(pss, '/pureNeApp/EC/debug_dump')
        print('Created debug_dump')

    def get_debug_dump(pss, dest):
        print('Transferring debug_dump')
        pss.get_file('/tmp/debug', dest, callback=progress)
        print('Transferred debug_dump')

    def clean_debug_dump(pss):
        print('Cleaning debug_dump')
        execute(pss, '/pureNeApp/EC/debug_dump clean')
        print('Cleaned debug_dump')

    try:
        create_debug_dump(pss)
        get_debug_dump(pss, dest)
        clean_debug_dump(pss)
    except Exception as e:
        print(e)
    finally:
        clean_debug_dump(pss)
        pss.close()

def collect_all_dump(pss, dest):

    def create_all_dump(pss):
        print('Creating all_dump')
        execute(pss, '/pureNeApp/EC/all_dump')
        print('Created all_dump')

    def get_all_dump(pss, dest):
        print('Transferring all_dump')
        pss.get_file('/pureNeApp/scratch/', dest, callback=progress)
        print('Transferred all_dump')

    def clean_all_dump(pss):
        print('Cleaning all_dump')
        execute(pss, 'cd /pureNeApp/scratch; rm -rf /pureNeApp/scratch/*')
        print('Cleaned all_dump')
    
    try:
        create_all_dump(pss)
        get_all_dump(pss, dest)
        clean_all_dump(pss)
    except Exception as e:
        print(e)
    finally:
        clean_all_dump(pss)
        pss.close()

def run(config):
    print(config)
    pss = PSSRoot(config['host'], config['port'], config['user'], config['pass'])
    pss.TIMEOUT = config['timeout']
    pss.open()
    if config['all']:
        collect_all_dump(pss, config['dest'])
    else:
        collect_debug_dump(pss, config['dest'])

def main():
    parser = get_parser()
    config = get_config(parser.parse_args())    
    run(config)

if __name__ == '__main__':
    main()