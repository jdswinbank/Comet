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

Given the raw benchmark data, you can re-generate the aggregates as part of
the build. The data is available for download through the `GitHub Release
system <https://github.com/jdswinbank/Comet/releases/>`_.  Once the data is
installed, use the following CMake invocation::

  $ cmake -DBENCHMARK_DATA=${PATH_TO_DATA} ..

A brief note on `Minted
<http://www.ctan.org/tex-archive/macros/latex/contrib/minted/>`_. This
requires that LaTeX be invoked with the ``-shell-escape`` option to enable it
to invoke ``pygmentize``. This is not supported by `The ArXiv
<http://www.arxiv.org>`_. We can work around this by directly invoking
``pygmentize`` and copy & pasting the results into the manuscript. Put the
code to highlight in ``${filename}``, then run::

  $ pygmentize -f latex -l python ${filename}

Copy and paste the resulting ``Verbatim`` environment into the manuscript.
Something like this emulates Minted's spacing and rules reasonably well::

  \begin{listing}[t]
  \hrulefill
  \vspace{-10pt}
  \begin{Verbatim}
  ...
  \end{Verbatim}
  \vspace{-15pt}
  \hrulefill
  ...
  \end{listing}

For the XPath queries::

  \begin{listing}[H]
  \begin{Verbatim}
  ...
  \end{Verbatim}
  \vspace{-15pt}
  \hrulefill
  \vspace{-9pt}
  ...
  \end{listing}
