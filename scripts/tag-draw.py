#!/usr/bin/env python2.7

import argparse
import sys
from tagperf import tagplt

def run(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf_file')
    parser.add_argument(
        '-o', '--out-dir', help='output dir (default %(default)s)', 
        default='plots')
    args = parser.parse_args(sys.argv[1:])
    tagplt.make_plots(args.hdf_file, args.out_dir)

if __name__ == '__main__': 
    run()
