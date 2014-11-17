#!/usr/bin/env python3

import argparse
import sys

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

    from tagperf import ctaging
    print('making ctag plots')
    ctaging.peters_plots(args.hdf_file, 'REJREJ_CACHE.h5', args.out_dir,
                         args.ext)

if __name__ == '__main__':
    run()
