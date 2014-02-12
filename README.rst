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
for publishing VOEvents to a remote broker.

Comet is developed targeting Python 2.6 and 2.7. It depends upon `Twisted
<http://twistedmatrix.com/>`_, `lxml <http://lxml.de/>`_ and `ipaddr-py
<https://code.google.com/p/ipaddr-py/>`_.

See the `Comet website
<http://comet.transientskp.org>`_ for further details, or go straight to the
`documentation <http://comet.readthedocs.org/>`_.

Final words
-----------

Comet is developed by `John Swinbank <http://swinbank.org/>`_ as
part of the `LOFAR <http://www.lofar.org/>`_ `Transients Key Project
<http://www.transientskp.org/>`_. Comments and corrections welcome.

See also the `Dakota VOEvent Tools <http://voevent.dc3.com/>`_ for an
alternative high-quality VOEvent distribution system.
