=======================
Comet: A VOEvent Broker
=======================

Manuscript for submission to Astronomy and Computing.

Requirements to build a PDF:

* LaTeX
* Python
* NumPy
* Matplotlib
* CMake
* Twisted

Use CMake to build the document based on pre-computed benchmark aggregates::

  $ mkdir build
  $ cd build
  $ cmake ..
  $ make

Given the raw benchmark data (several hundred MiB; available for download
separately), you can re-generate the aggregates as part of the build. Use the
following CMake invocation::

  $ cmake -DBENCHMARK_DATA=${PATH_TO_DATA} ..
