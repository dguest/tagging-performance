#!/usr/bin/env python3

import argparse
import sys

def run():
    cache = 'REJREJ_CACHE.h5'
    d = '(default %(default)s)'
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf_file')
    parser.add_argument(
        '-o', '--out-dir', help='output dir ' + d,
        default='plots')
    parser.add_argument(
        '-e', '--ext', help='plot extension ' + d,
        default='.pdf')
    parser.add_argument(
        '-c', '--cache', help='cache for rejrej plots ' + d, default=cache)
    args = parser.parse_args(sys.argv[1:])

    from tagperf import ctaging, cutplane, peters
    from tagperf.bullshit import helvetify
    print('making ctag plots')
    helvetify()
    peters.peters_cross_check(args.hdf_file, args.out_dir, args.ext)
    cutplane.draw_cut_plane(args.hdf_file, args.out_dir, args.ext)
    ctaging.peters_plots(args.hdf_file, args.cache, args.out_dir, args.ext)
    ctaging.make_peters_1d(args.hdf_file, args.out_dir, args.ext)

if __name__ == '__main__':
    run()
