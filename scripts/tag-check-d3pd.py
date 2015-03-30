#!/usr/bin/env python3
"""
Script to run some cross-checks on d3pd hists
"""

import argparse
import sys
import h5py
import numpy as np

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('hdf_file')
    return parser.parse_args(sys.argv[1:])

def _get_eff(dataset, cuts):
    mins = dataset.attrs['min']
    maxes = dataset.attrs['max']
    bounds = zip(mins, maxes)
    n_bins = [x - 2 for x in dataset.shape]
    array = np.asarray(dataset)
    bin_edges = [np.linspace(*b, num=n) for b, n in zip(bounds, n_bins)]
    slices = []
    for cutval, edges in zip(cuts, bin_edges):
        dists = np.abs(edges - cutval)
        closest = np.argmin(dists)
        slices.append(slice(closest, None))
    passing = array[slices].sum()
    total = array.sum()
    return passing / total

def _check_tagger_eff(h5, tagger, cuts):
    for flav in ['U','C','B']:
        eff = _get_eff(h5[flav]['ctag']['all'][tagger], cuts)
        print(flav, eff, 1/eff)

def run():
    args = get_args()
    with h5py.File(args.hdf_file, 'r') as h5:
        print('old jfit OP')
        _check_tagger_eff(h5, 'jfit',  [-0.82, -1])
        print('new jfit OP (moved to keep the same c-eff, and b-rej')
        _check_tagger_eff(h5, 'jfit',  [-1.4, -0.9])
        print('old jfc OP')
        _check_tagger_eff(h5, 'jfc', [0.95, -0.9])
        print('new jfc OP (moved to keep the same c-eff, and b-rej')
        _check_tagger_eff(h5, 'jfc', [0.42, -0.61])
if __name__ == '__main__':
    run()
