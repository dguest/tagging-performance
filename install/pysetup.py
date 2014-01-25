#!/usr/bin/env python2.7

import site
from os.path import isfile, isdir, join, abspath, split
import os, sys
import argparse

def here_path(): 
    return '/'.join(abspath(__file__).split('/')[:-2] + ['python'])

def pth_file_path(): 
    usr_path = site.getusersitepackages()
    pth_file = join(usr_path, 'perf_hists.pth')
    return pth_file

def add_path(): 
    pth_file_dir, pth_file = split(pth_file_path())
    usr_path = here_path()
    if not isdir(pth_file_dir): 
        os.makedirs(pth_file_dir)
    with open(join(pth_file_dir,pth_file),'w') as pfile: 
        pfile.write(here_path())

def rm_path(): 
    if isfile(pth_file_path()): 
        os.remove(pth_file_path())
    

if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices={'install','remove'})
    args = parser.parse_args(sys.argv[1:])
    {'install': add_path, 'remove': rm_path}[args.action]()
