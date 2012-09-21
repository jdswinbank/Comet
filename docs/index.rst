Comet
=====

Comet is a Python implementation of the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_ (VTP).

The core of Comet is a multi-functional VOEvent broker. It is capable of
receiving events either by subscribing to one or more remote brokers or by
direct connection from authors, and can then both process those events locally
and forward them to its own subscribers. In addition, Comet provides a tool
for publishing VOEvents to a remote broker.

.. toctree::
   :maxdepth: 2

   installation
   usage/index
   filtering
   handlers
   authentication
   appendix/index

Comet is developed by `John Swinbank <http://swinbank.org/>`_ as part of the
`LOFAR Transients Key Project <http://www.transientskp.org/>`_. The latest
version is always available from `the project website
<http://comet.transientskp.org/>`_.

Feedback is always welcome. For bug reports and feature requests, please use
the `issue tracker <https://github.com/jdswinbank/Comet/issues>`_.

.. Indices and tables
   ==================

..   * :ref:`genindex`
     * :ref:`modindex`
     * :ref:`search`

