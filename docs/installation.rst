Obtaining and Installing Comet
==============================

Comet is intended to easy to install, but does have a few dependencies. Your
feedback as to how this process could be streamlined is welcome.

Requirements
------------

Comet is developed targeting Python 2.6 and 2.7. It depends upon:

* `Twisted <http://twistedmatrix.com/>`_ (versions ≥ 11.1.0)
* `lxml <http://lxml.de/>`_ (versions ≥ 2.3)
* `zope.interface <http://docs.zope.org/zope.interface/>`_ (versions ≥ 3.6.0)
* `ipaddr-py <https://code.google.com/p/ipaddr-py/>`_.

If the optional support for :ref:`authentication <sec-authentication>` is to
be enabled, `PyGPGME <https://launchpad.net/pygpgme>`_ (and all of its
dependencies) is also required.

How you make these dependencies available on your system is up to your (or,
perhaps, to your system administrator). However, the author strongly suggests
you might start by taking a look at `virtualenv
<http://www.virtualenv.org/>`_.

Downloading
-----------

The latest released version of Comet is available to download from `its
website <http://comet.transientskp.org>`_.

Comet is hosted on `GitHub <http://www.github.com/jdswinbank/Comet>`_. The
latest version of the source can be obtained using `git
<http://git-scm.org>`_::

  $ git clone https://github.com/jdswinbank/Comet.git

Installation
------------

Comet includes a `distutils <http://docs.python.org/distutils/index.html>`_
setup script which can be used for installation. To install in your
system-default location, run::

  $ python setup.py install

A number of other options are available: see also::

  $ python setup.py --help

Testing
-------

After installation, you should check that Comet is properly installed. The
Twisted framework Comet used by Comet makes this easy with its ``trial`` tool.
Simply run::

  $ trial comet

No failures or errors are expected in the test suite. If you see a problem,
please contact the author for help. Note that some tests may be skipped if you
chose not to install PyGPGME.
