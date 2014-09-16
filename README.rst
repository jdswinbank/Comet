=====
Comet
=====
----------------
A VOEvent Broker
----------------

Comet is a Python implementation of the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_ (VTP).

The core of Comet is a multi-functional VOEvent broker. It is capable of
receiving events either by subscribing to one or more remote brokers or by
direct connection from authors, and can then both process those events locally
and forward them to its own subscribers. In addition, Comet provides a tool
for publishing VOEvents to a remote broker.  See the `website
<http://comet.transientskp.org>`_ for further details and documentation.

Comet is developed targeting Python 2.6 and 2.7. It depends upon `Twisted
<http://twistedmatrix.com/>`_, `lxml <http://lxml.de/>`_ and `ipaddr-py
<https://code.google.com/p/ipaddr-py/>`_.

This repository contains the following branches:

``master``
    Contains the current working version of the code, scheduled to become the
    next release.

``release-X.Y``
    Branches corresponding to specific Comet releases.

``gpg``
    Work-in-progress test version of Comet incorporating OpenPGP support.

``paper``
    A manuscript describing Comet published `Astronomy and
    Computing <http://www.journals.elsevier.com/astronomy-and-computing/>`_.

Comet is developed by `John Swinbank <http://swinbank.org/>`_ as part of the
`LOFAR <http://www.lofar.org/>`_ `Transients Key Project
<http://www.transientskp.org/>`_. It is indexed by the `Astrophysics Source
Code Library <http://asterisk.apod.com/wp/>`_ as `ascl:1404.008
<http://ascl.net/1404.008>`_.

If you make use of Comet in published research, please cite `Swinbank (2014)
<http://dx.doi.org/10.1016/j.ascom.2014.09.001>`_.

Comments and corrections welcome.
