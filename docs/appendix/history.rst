.. _sec-history:

Release History
===============

Version 1.0.x
-------------

1.0.0 (2012-08-27) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.0>`__]
   Initial public release

1.0.1 (2012-08-28) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.1>`__]
   Fix for badly formed XML ``Transport`` element.

1.0.2 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.2>`__]
   Add a ``requirements.txt`` file and specify the installation requirements
   in ``setup.py``. This makes installation easier, but changes nothing on an
   installed system.

1.0.3 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.3>`__]
   Update ``MANIFEST.in`` so that ``requirements.txt`` is included in the
   distribution. This changes nothing on an installed system.

1.0.4 (2013-11-13) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.4>`__]
   ``comet-sendvo`` will choose its Python interpreter based on the
   environment.

Version 1.1.x
-------------

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

Future Plans
------------

Cryptographic authentication of VOEvent messages and subscribers.
