Event Publisher
===============

``comet-sendvo`` is a simple event publisher: it forwards messages from an
author to a broker.

After installation, it should be possible to execute ``comet-sendvo`` directly
from the command line. Use the ``--help`` option to display a brief usage
message::

  $ comet-sendvo --help
  usage: comet-sendvo [-h] [--verbose] target event

  positional arguments:
    target         Address of receiver to which to send as an endpoint string.
    event          File containing event text to send; '-' for stdin.

  optional arguments:
    -h, --help     show this help message and exit
    --verbose, -v  Increase verbosity (may be specified more than once).

To use, simply supply ``comet-sendvo`` with the details of the broker to which
to submit the event (the ``target`` argument) and with the text of a VOEvent
message to send (the ``event`` argument).

``target`` accepts a string describing a `Twisted client endpoint`_. For
example, possible targets include:

- ``tcp:hostname:8098``, to make a TCP connection on port 8099 to the hostname
  ``hostname``;
- ``unix:/some/file/name``, to connect over a `Unix domain socket`_ at path
  :file:`/some/file/name`.

For convenience, a TCP connection on port 8098 is assumed if alternatives are
not explicitly specified; thus, a target of ``example.voevent.broker.com`` is
equivalent to ``tcp:example.voevent.broker.com:8098``.

``event`` accepts the name of a file containing the text of the event to be
sent. The file must exist on the filesystem. Alternatively, the special value
``-`` may be specified to indicate that event text should be read from
standard input.

Thus, for example, the following invocations are equivalent::

  $ comet-sendvo tcp:remote.invalid:8098 - < voevent_to_publish.xml

and::

  $ comet-sendvo remote.invalid voevent_to_publish.xml

.. _Twisted client endpoint: https://twistedmatrix.com/documents/current/core/howto/endpoints.html
.. _Unix domain socket: https://en.wikipedia.org/wiki/Unix_domain_socket
