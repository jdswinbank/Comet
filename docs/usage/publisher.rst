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
    -f, --file=             Where to read XML text (- is stdin). [default: -]
        --version           Display Twisted version and exit.
        --help              Display this help and exit.

Basic usage is straightforward: simply supply ``comet-sendvo`` with the
details of the broker to connect to using the ``--host`` and ``--port``
options (or accept the defaults), and give it the text of a VOEvent either
directly on standard input or by giving the path to a file. For example::

  $ comet-sendvo --host=remote.invalid --port=8098 < voevent_to_publish.xml

Or::

  $ comet-sendvo -h remote.invalid -f voevent_to_publish.xml
