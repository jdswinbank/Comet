.. _sec-sendvo:

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
    -h, --host=    Host to send to. [default: localhost]
    -p, --port=    Port to send to. [default: 8098]
    -f, --file=    Where to read XML text (- is stdin). [default: -]
    -s, --sign=    Sign event. Requires argument <key-id>:<passphrase-file>.
        --version  Display Twisted version and exit.
        --help     Display this help and exit.

Basic usage is straightforward: simply supply ``comet-sendvo`` with the
details of the broker to connect to using the ``--host`` and ``--port``
options (or accept the defaults), and give it the text of a VOEvent either
directly on standard input or by giving the path to a file. For example::

  $ comet-sendvo --host=remote.invalid --port=8098 < voevent_to_publish.xml

Or::

  $ comet-sendvo -h remote.invalid -f voevent_to_publish.xml

It is also possible to configure ``comet-sendvo`` to cryptographically sign
the event before sending it by supplying the ``--sign`` option. For details on
the implementation and implications of this feature, see :ref:`the section on
authentication <sec-authentication>`.  Note that the ``--sign`` option
requires two arguments, separated by a colon (``:``): the (hexadecimal) key ID
to be used for signing and the name of a file from which the passphrase used
to unlock the key can be read.  For example::

  $ cat secret
  my-gpg-passphrase
  $ comet-sendvo --sign AEA9D2CE:secret < voevent_to_publish.xml
