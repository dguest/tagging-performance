#!/usr/bin/env bash 

if [[ ! $1 ]]
then 
    echo 'need a file to run on' >&2 
    exit 1
fi

out=${1%.root}.h5
rm -f $out

supp=--suppressions=${ROOTSYS}/etc/root/valgrind-root.supp
leakch=--leak-check=full
valgrind $supp $leakch tag-perf-hists -t $1 -o $out 