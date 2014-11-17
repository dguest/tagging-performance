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

    from tagperf import ctaging, cutplane
    from tagperf.bullshit import helvetify
    print('making ctag plots')
    helvetify()
    cache = 'REJREJ_CACHE.h5'
    # ctaging.peters_cross_check(args.hdf_file, args.out_dir, args.ext)
    cutplane.draw_cut_plane(args.hdf_file, args.out_dir, args.ext)
    # ctaging.peters_plots(args.hdf_file, cache, args.out_dir, args.ext)
    # ctaging.make_peters_1d(args.hdf_file, args.out_dir, args.ext)

if __name__ == '__main__':
    run()
