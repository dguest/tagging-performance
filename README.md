# Jet Tagging Performance Plots

This is to test things and compare jet tagger performance. 

## Required Packages 

This package requires [ROOT][0] to read ATLAS data. Fortunately the use is minimal: no fancy PyROOT or Roofit installation required. 

Unfortunately there are a few other dependencies. The upshot is that these packages are fairly standard for python data analysis, and thus quite easy to use. They are generally installed using something like `python3.3 setup.py install`.  

- [Python 3.3][1] is used throughout (when installing from source, use `--enable-shared`)
- [Numpy][4] 
- HDF5 is used for binary data storage: 
 + [HDF5][2] basic library (be sure to install with `--enable-cxx`)
 + [h5py][3] for python bindings
- [matplotlib][7] for plotting 

Optional: 

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
