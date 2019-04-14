Comet
=====

`VOEvent`_ is the `International Virtual Observatory Alliance`_ standard for
describing transient celestial events. Comet is an implementation of the
`VOEvent Transport Protocol`_, which provides a mechanism for fast and
reliable distribution of VOEvents to the community.  Comet enables you to
subscribe to and act upon real-time streams of ongoing events, to use filters
to select only events relevant to your science case, and to publish your own
events to the global VOEvent backbone.

.. toctree::
   :maxdepth: 2

   installation
   usage/index
   filtering
   handlers
   history
   credits
   appendix/index

Released versions of Comet are available for :doc:`download <history>`,
while the latest development version can be obtained from the `GitHub
repository <https://github.com/jdswinbank/Comet>`_.

Feedback is always welcome. For bug reports and feature requests, please use
the `issue tracker <https://github.com/jdswinbank/Comet/issues>`_.

.. _VOEvent: http://www.ivoa.net/documents/VOEvent/index.html
.. _International Virtual Observatory Alliance: http://www.ivoa.net/
.. _VOEvent Transport Protocol: http://www.ivoa.net/documents/VOEventTransport/index.html
