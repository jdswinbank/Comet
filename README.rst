=======================
Comet: A VOEvent Broker
=======================

Manuscript accepted for publication in Astronomy and Computing.

Requirements to build a PDF:

* LaTeX
* Python
* NumPy
* Matplotlib
* CMake
* Twisted
* Pygments

Use CMake to build the document based on pre-computed benchmark aggregates::

  $ mkdir build
  $ cd build
  $ cmake ..
  $ make

Given the raw benchmark data, you can re-generate the aggregates as part of
the build. The data is available for download through the `GitHub Release
system <https://github.com/jdswinbank/Comet/releases/>`_.  Once the data is
installed, use the following CMake invocation::

  $ cmake -DBENCHMARK_DATA=${PATH_TO_DATA} ..
