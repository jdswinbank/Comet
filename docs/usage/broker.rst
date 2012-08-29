Broker
======

Twisted Applications
--------------------

The Comet broker is implemented as a `Twisted application
<http://www.twistedmatrix.com/>`_. This means that it is not invoked directly
on the command line, but rather using the ``twistd`` tool provided as part
of Twisted.

``twistd`` provides a wide range of generic configuration options related to
daemonizing, logging, profiling, and so on. This fall outside the scope of
this documentation, but the interested reader is encouraged to familiarize
themselves with the contents of ``twistd(1)``.

It is worth noting that, by default, processes invoked with ``twistd`` are
immediately daemonized. That is, ``twistd`` is invoked, it returns control to
your shell prompt almost immediately, but Comet is now running in the
background. This is generally very convenient, but sometimes it's useful to
have the application run in the foreground when testing and debugging: to
achieve this, invoke ``twistd -n``.

Invoking Comet
--------------

Specify name of the Twisted application to run after ``twistd`` and its
options. In this case, we run ``comet``, and pass it the ``--help`` option to
provide a brief usage message::

  $ twistd comet --help
  Usage: twistd [options] comet [options]
  Options:
    -r, --receive           Listen for TCP connections from authors.
    -b, --broadcast         Re-broadcast VOEvents received.
    -v, --verbose           Increase verbosity.
    -q, --quiet             Decrease verbosity.
        --sender-auth       Only accept signed events from authors
        --subscriber-auth   Require subscribers to authenticate.
        --local-ivo=        [default: ivo://comet.broker/default_ivo]
        --eventdb=          Event database root. [default: /tmp]
        --receive-port=     TCP port for receiving events. [default: 8098]
        --broadcast-port=   TCP port for broadcasting events. [default: 8099]
        --whitelist=        Network to be included in submission whitelist.
                            [default: 0.0.0.0/0]
        --remote=           Remote broadcaster to subscribe to (host[:port]).
        --filter=           XPath filter applied to events broadcast by remote.
        --action=           Add an event handler.
        --cmd=              Spawn external command on event receipt.
        --key-id=           Subscriber OpenPGP key ID.
        --passphrase-file=  File containing passphrase to unlock OpenPGP key.
        --help              Display this help and exit.
        --version           Display Twisted version and exit.

Basic Modes of Operation
++++++++++++++++++++++++

If the ``--receive`` option is supplied, Comet will fulfil the Broker role in
an Author to Broker connection. In other words, it will listen for TCP
connections from remote authors and accept events for distribution. The TCP
port on which Comet will listen may be specified with the ``--receive-port``
option.

If the ``--broadcast`` option is supplied, Comet will listen for Subscribers
to connect and then it will fulfil the Broker role in a Broker to Subscriber
connection with each of the Subscribers. Any VOEvents received (either by
direct connection from authors, or by subscribing to remote brokers) are
rebroadcast to subscribers. The TCP port on which Comet will allow subscribers
to connect may be specified with the ``--broadcast-port`` option.

If one or more ``--remote`` options are supplied, Comet will subscribe to the
remote host specified and fulfil the Subscriber role in the resulting Broker
to Subscriber connection. If just given a hostname Comet will attempt to
subscribe on port 8099. Optionally, a different port may be specified by
appending it to the hostname, separated by a ``:``.

A single Comet daemon will accept any combination of ``--receiver``,
``--broadcast`` and one or more ``--remote`` options and play all of the
specified roles simultaneously. If none of ``--receiver``, ``--broadcast`` or
``--remote`` are supplied, there is no work to be done and Comet will exit
immediately.

Identification
++++++++++++++

Whatever the mode of operation, Comet identifies itself by means of an
*International Virtual Observatory Resource Name* or *IVORN*: see the `VOEvent
standard <http://www.ivoa.net/Documents/VOEvent/index.html>`_ for details. You
should specify some appropriate IVORN for your site using the ``--local-ivo``
option.

VOEvent Network Maintenance
+++++++++++++++++++++++++++

In order to prevent looping on the network (ie, two brokers exchanging the
same event ad infinitum), a database of previously seen event is maintained.
This database is written to the filesystem in the location specified by the
``--eventdb`` option. Events which are recorded in the database are not
forwarded by Comet. This is important: looping would degrade the quality of
the VOEvent network for all users! Note that events persist in the database
for 30 days, after which they are expired to save space.

Receiver Options
++++++++++++++++

When acting as a receiving broker (with ``--receive``), Comet will only accept
new events for publication from hosts which have been specified as
"whitelisted". Hosts (or, indeed, networks) may be included in the whitelist
using the ``--whitelist`` option. This option accepts either `CIDR
<https://en.wikipedia.org/wiki/CIDR_notation>`_ or dot-decimal notation
including a subnet mask. For example, ``--whitelist 127.0.0.1/32`` and
``--whitelist 127.0.0.1/255.255.255.255`` both permit the local host to submit
events to the broker. This option may be specified multiple times and the
results are cumulative. To accept submissions from any host, specify
``--whitelist 0.0.0.0/0``; this is the default if no ``--whitelist`` option is
supplied.

It is also possible to configure Comet to only accept cryptographically signed
event submissions from authors. This functionality is enabled by invoking
Comet with the ``--sender-auth`` option. For a discussion of the
implementation and implications of this, see the section on
:ref:`authentication <sec-authentication>`.

Broadcaster Options
+++++++++++++++++++

When Comet is configured to rebroadcast events to subscribers (with
``--broadcast``), it can optionally require those subscribers to
cryptographically identify themselves before they are eligible to receive
events. This is enabled with the ``--subscriber-auth`` option.  For a details
of the implementation and implications of this option, see the section on
:ref:`authentication <sec-authentication>`.

Subscriber Options
++++++++++++++++++

When subscribing to a remote broker (with ``--remote``), one or more filters
may be specified which limit the events which will be received. These filters
are specified with ``--filter``, in the form of `XPath 1.0
<http://www.w3.org/TR/xpath/>`_ expressions. The broker will evaluate the
expression against each event it processes, and only forward the event to the
subscriber if it produces a non-empty result. For more details see the section
on :ref:`filtering <sec-filtering>`.

Common Options
++++++++++++++

Custom code may be run to perform local processing on an event when it is
received. This is specifed by the ``--action`` option. For more details, see
the section on :ref:`event handlers <sec-handlers>`. These actions will be
taken whether Comet receives an event from an author (``--receive``) or an
upstream broker (``--remote``).

Similarly, received events may be sent to one or more external commands
for processing. These are specified using the ``--cmd`` option. They should
accept the event on standard input and perform whatever processing is required
before exiting. The standard output and error from the external process is
ignored.  If it returns a value other than 0, it will be logged as a failure.
Note that external commands are run in a separate thread, so will not block
the subscriber from processing new events; however, the user is nevertheless
responsible for ensuring that they terminate in a timely fashion.

The amount of information Comet writes to its log may be adjusted using the
``--verbose`` and ``--quiet`` options.
