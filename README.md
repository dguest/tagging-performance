# Jet Tagging Performance Plots

Package to compare jet tagger performance. 

The code is divided into two parts, each accessed by its own executable in
`scripts/`:

 - `tag-perf-hists`: fill histograms. The routine creates histograms from a D3PD
   and stores them as an HDF5 file. For basic usage see `tag-perf-hists -h`.
 - `tag-draw.py`: plot histograms. Draws all the histograms using the HDF5 file
   produced by `tag-perf-hists`.

## Installing

This code has been tested on Ubuntu 12.04, Mac OSX, SLC5, and SLC6. If your
default compiler doesn't support c++11, the `CXX` environment variable must
point to a compiler that does. Clone with 

    git clone --recursive <repository url>

Once you've cloned the repository, it should install with

    make

This should build the histogram filling executable and run `install/pysetup.py
install` which will add the local python modules to your python search path.

## Dependencies

### Histogram filling:

 - A compiler supporting c++11
 - [ROOT][0] (minimal: no fancy PyROOT or Roofit installation required)
 - [HDF5][2] (be sure to install with `--enable-cxx`)

### Plotting: 

These packages are fairly standard for python data analysis, and thus quite easy
to use. They are generally installed using something like `python3.3 setup.py
install`. Note that ROOT is **not** used (or required) for plotting.

- [Python 3.3][1] (when installing from source, use `--enable-shared`)
- [Numpy][4] 
- HDF5: 
 + [HDF5][2] basic installation 
 + [h5py][3] for python bindings
- [matplotlib][7] for plotting 

### Optional Plotting: 

- [scipy][8] for various functions (that can be disabled)
- [pyyaml][5] for [yaml][6] (if not installed use json instead)

[0]: http://root.cern.ch/drupal/content/downloading-root
[1]: http://www.python.org/getit/
[2]: http://www.hdfgroup.org/HDF5/release/obtainsrc.html
[3]: http://www.h5py.org/
[4]: https://pypi.python.org/pypi/numpy
[5]: http://pyyaml.org/wiki/PyYAML#DownloadandInstallation
[6]: http://www.yaml.org/
[7]: http://matplotlib.org/downloads.html
[8]: http://sourceforge.net/projects/scipy/files/
