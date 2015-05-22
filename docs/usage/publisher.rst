Event Publisher
===============

``comet-sendvo`` is a simple event publisher: it forwards messages from an
author to a broker.

After installation, it should be possible to execute ``comet-sendvo`` directly
from the command line. Use the ``--help`` option to display a brief usage
message::

  $ comet-sendvo --help
  Usage: comet-sendvo [options]
  Options:
    -h, --host=             Host to send to. [default: localhost]
    -p, --port=             Port to send to. [default: 8098]
        --version           Display Twisted version and exit.
        --help              Display this help and exit.

Basic usage is straightforward: simply supply ``comet-sendvo`` with the details
of the broker to connect to using the ``--host`` and ``--port`` options (or
accept the defaults), and give it the the path to an XML file containing a
VOEvent message. For example::

  $ comet-sendvo --host=remote.invalid --port=8098 voevent_to_publish.xml

It is also possible to use ``comet-sendvo`` to submit ``tar`` archives
containing multiple events to a broker. Note that this is a Comet-specific
extension to the regular protocol, and may not be supported by the broker you
are submitting to. The syntax is exactly the same, but note that Comet listens
for bulk submissions on a different TCP port---by default, it uses 8097---so
you will have to specify this::

  $ comet-sendvo -h remote.invalid --port=8097 voevent_archive.tar.gz

Note that archives compressed with ``gzip`` and ``bzip2`` are supported.
