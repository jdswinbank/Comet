.. _sec-history:

Release History
===============

See the :ref:`release procedure <sec-release>` section for more details on
version numbering and how releases are made.

Version 1.2.x
-------------

1.20 (2014-08-26) [`Download <//github.com/jdswinbank/Comet/tarball/1.2.0>`__]
    When subscribing to a remote broker, we wait for a short period after the
    initial connection is made before marking it as successful. This means
    that if the broker rapidly drops the connection (e.g. due to an
    authentication failure), we retry the connection with an exponential
    back-off rather than an immediate reconnection (`GitHub #29`_).

    Timestamps in ``iamalive`` messages are marked as being in UTC.

    ``authenticate`` messages which specify XPath filters are schema
    compliant (`GitHub #31`_).

    Subscriber refuses to start if an XPath ``--filter`` is specified with
    invalid syntax (`GitHub #33`_).

    Require that a valid IVOA identifier (IVORN) be supplied by the end user
    when starting Comet rather than relying on a default.

    Require that events submitted to the broker by authors have valid IVORNs.

.. _GitHub #29: https://github.com/jdswinbank/Comet/issues/29
.. _GitHub #31: https://github.com/jdswinbank/Comet/issues/31
.. _GitHub #33: https://github.com/jdswinbank/Comet/issues/33


Version 1.1.x
-------------

1.1.2 (2014-08-26) [`Download <//github.com/jdswinbank/Comet/tarball/1.1.2>`__]
    Fix a bug which could result in malformed event IVORNs exhausting the
    available resources and ultimately rendering Comet unable to process more
    events (`GitHub #34`_).

1.1.1 (2014-07-08) [`Download <https://github.com/jdswinbank/Comet/tarball/1.1.1>`__]
    Fix a bug which could result in the same VOEvent message being processed
    multiple times (`GitHub #30`_).

    Add compatibility with DBM-style databases which do not provide an
    ``.items()`` method.

1.1.0 (2014-02-26) [`Download <https://github.com/jdswinbank/Comet/tarball/1.1.0>`__]
    Improved documentation.

    Interval between broadcast test events is user configurable, and they may
    be disabled. See the ``--broadcast-test-interval`` option.

    Test events now include details of the version of Comet used to generate
    them.

    Event handler plugin system reworked. Plugins may now take command line
    options. See the :ref:`event handler documentation <sec-handlers>` for
    details. Note that the syntax for invoking the ``print-event`` handler has
    changed (now ``--print-event`` rather than ``--action=print-event``).

    Plugin which writes events received to file (``--save-event``).

.. _GitHub #30: https://github.com/jdswinbank/Comet/issues/30
.. _GitHub #34: https://github.com/jdswinbank/Comet/issues/34


Version 1.0.x
-------------

1.0.4 (2013-11-13) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.4>`__]
   ``comet-sendvo`` will choose its Python interpreter based on the
   environment.

1.0.3 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.3>`__]
   Update ``MANIFEST.in`` so that ``requirements.txt`` is included in the
   distribution. This changes nothing on an installed system.

1.0.2 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.2>`__]
   Add a ``requirements.txt`` file and specify the installation requirements
   in ``setup.py``. This makes installation easier, but changes nothing on an
   installed system.

1.0.1 (2012-08-28) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.1>`__]
   Fix for badly formed XML ``Transport`` element.

1.0.0 (2012-08-27) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.0>`__]
   Initial public release


Future Plans
------------

Cryptographic authentication of VOEvent messages and subscribers.
