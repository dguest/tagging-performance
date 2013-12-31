#!/usr/bin/env python2.7

import argparse
import sys
from tagperf import tagroc
from tagperf import tagpt

def run(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf_file')
    parser.add_argument(
        '-o', '--out-dir', help='output dir (default %(default)s)', 
        default='plots')
    args = parser.parse_args(sys.argv[1:])
    tagroc.make_plots(args.hdf_file, args.out_dir)
    tagpt.make_plots(args.hdf_file, args.out_dir)

if __name__ == '__main__': 
    run()
