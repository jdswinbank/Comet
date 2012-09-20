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
    -s, --sign              Sign event with GnuPG.
    -h, --host=             Host to send to. [default: localhost]
    -p, --port=             Port to send to. [default: 8098]
    -f, --file=             Where to read XML text (- is stdin). [default: -]
        --passphrase-file=  File containing passphrase to unlock OpenPGP key.
        --key=              GnuPG key id.
        --version           Display Twisted version and exit.
        --help              Display this help and exit.

Basic usage is straightforward: simply supply ``comet-sendvo`` with the
details of the broker to connect to using the ``--host`` and ``--port``
options (or accept the defaults), and give it the text of a VOEvent either
directly on standard input or by giving the path to a file. For example::

  $ comet-sendvo --host=remote.invalid --port=8098 < voevent_to_publish.xml

Or::

  $ comet-sendvo -h remote.invalid -f voevent_to_publish.xml

It is also possible to configure ``comet-sendvo`` to cryptographically sign
the event before sending it. For details on the implementation and
implications of this feature, see :ref:`the section on authentication
<sec-authentication>`. Here, simply note that it is possible to specify both
whether signing is required (using the ``--sign`` option) and the particular
key to be used (``--key``) on the command line. Specifying the passphrase is a
little more complex: for security reasons, rather than accepting it on the
command line, ``comet-sendvo`` expects you to write it into a file and supply
the filename instead. This prevents the passphrase from being read out of the
system process table by other users. Obviously, the file you store your
passphrase in should only be readable by the user invoking ``comet-sendvo``.
For example::

  $ cat secret
  my-gpg-passphrase
  $ comet-sendvo -s --key=AEA9D2CE --passphrase-file=secret < voevent_to_publish.xml
