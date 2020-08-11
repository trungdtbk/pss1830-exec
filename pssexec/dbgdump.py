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
    parser.add_argument('-d', '--dest', help="Destination directory. Default: current dir", default=".")
    parser.add_argument('-w', '--timeout', help="Timeout to wait for result. Default: 20 secs", default=15, type=int)
    return parser

def get_config(args):
    config = vars(args)    
    return config

def progress(size, sent):
    sys.stdout.write("Transfered: %.2f%%   \r" % (float(sent)/float(size)*100))

def get_debug_dump(pss, dest='.'):
    print('Collecting debug dump\n')
    scp = pss.client.open_sftp()
    scp.chdir('/tmp/debug')
    files = scp.listdir()
    path = os.path.join(dest, 'debugdump-%s' % pss.host)
    try:
        os.mkdir(path)
    except:
        pass
    for f in files:
        local_file = os.path.join(path, f)
        print('Downloading: %s' % f)
        scp.get('/tmp/debug/%s' % f, local_file, progress)
    print('\nCollected debugdump to: %s' % path)

def create_debug_dump(pss):
    print('Creating debug dump')
    for line in pss.execute('/pureNeApp/EC/debug_dump'):
        print(line, end="")
    print('\nDebug dump created')

def clean_debug_dump(pss):
    print('Removing debug dump')
    for l in pss.execute('/pureNeApp/EC/debug_dump clean'):
        print(l)
    print('Removed debugdump')

def run(config):
    print(config)
    pss = PSSRoot(config['host'], config['port'], config['user'], config['pass'])
    pss.TIMEOUT = config['timeout']
    pss.open()
    try:
        create_debug_dump(pss)
        get_debug_dump(pss, config['dest'])
    except Exception as e:
        print(e)
    finally:
        clean_debug_dump(pss)
    pss.close()

def main():
    parser = get_parser()
    config = get_config(parser.parse_args())    
    run(config)

if __name__ == '__main__':
    main()