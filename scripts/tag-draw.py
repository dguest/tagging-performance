#!/usr/bin/env python3.3

import argparse
import sys
from tagperf import tagroc
from tagperf import tagpt
from tagperf import ctag

def run(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf_file')
    parser.add_argument(
        '-o', '--out-dir', help='output dir (default %(default)s)', 
        default='plots')
    parser.add_argument(
        '-e', '--ext', help='plot extension (default %(default)s)', 
        default='.pdf')
    args = parser.parse_args(sys.argv[1:])
    ctag.make_plots(args.hdf_file, 'cache.h5', args.out_dir, args.ext)
    # tagroc.make_plots(args.hdf_file, args.out_dir, args.ext)
    # tagpt.make_plots(args.hdf_file, args.out_dir, args.ext)

if __name__ == '__main__': 
    run()
