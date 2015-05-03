Obtaining and Installing Comet
==============================

Installation using pip
----------------------

The latest version of Comet and all of the tools it depends upon can be
installed using `pip <http://www.pip-installer.org/>`_. It is generally a good
idea to use `virtualenv <http://www.virtualenv.org/>`_ to create an isolated,
self-contained installation::

  $ virtualenv comet
  $ . comet/bin/activate
  $ pip install comet

Manual installation
-------------------

Requirements
^^^^^^^^^^^^

Comet is developed targeting Python 2.6 and 2.7. It depends upon:

* `Twisted <http://twistedmatrix.com/>`_ (version 11.1.0 or later)
* `lxml <http://lxml.de/>`_ (version 2.3 or later)
* `zope.interface <http://docs.zope.org/zope.interface/>`_ (versions 3.6.0 or later)
* `py2-ipaddress <https://bitbucket.org/kwi/py2-ipaddress/>`_.

How you make these dependencies available on your system is up to your (or,
perhaps, to your system administrator). However, the author strongly suggests
you might start by taking a look at `virtualenv
<http://www.virtualenv.org/>`_.

Downloading
^^^^^^^^^^^

See the :ref:`release history <sec-history>` to obtain the latest version of
Comet or check out the source from the `GitHub repository
<http://www.github.com/jdswinbank/Comet>`_. The latest version of the source
can be obtained using `git <http://git-scm.org>`_::

  $ git clone https://github.com/jdswinbank/Comet.git

Installation
^^^^^^^^^^^^

Comet includes a `distutils <http://docs.python.org/distutils/index.html>`_
setup script which can be used for installation. To install in your
system-default location, run::

  $ python setup.py install

A number of other options are available: see also::

  $ python setup.py --help

Testing
-------

After installation, you should check that Comet is working properly. The
Twisted framework used by Comet makes this easy with its ``trial`` tool.
Simply run::

  $ trial comet

No failures or errors are expected in the test suite. If you see a problem,
please contact the author for help.
