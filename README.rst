=====
Comet
=====
----------------
A VOEvent Broker
----------------

Comet is designed to serve as a development testbed for rapid prototyping of
and experimentation with VOEvent transport systems. Currently, it partially
implements the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_ (VTP).

The core of Comet is a multi-functional VOEvent broker. It is capable of
receiving events either by subscribing to one or more remote brokers or by
direct connection from authors, and can then both process those events
locally and forward them to its own subscribers.

In addition, Comet provides a tool for publishing VOEvents to a remote broker.

Requirements
------------

Comet is developed targeting Python 2.6 and 2.7. It depends upon `Twisted
<http://twistedmatrix.com/>`_ (versions >= 11.1.0), `lxml <http://lxml.de/>`_
(versions >= 2.3) and `ipaddr-py <https://code.google.com/p/ipaddr-py/>`_.

Installation
------------

A `distutils <http://docs.python.org/library/distutils.html>`_ ``setup.py``
script is included. To install in your system-default location, simply run::

  $ python setup.py install

See also::

  $ python setup.py --help

for more details.

Testing
-------

After installation, run the test suite to check that Comet is ready to go. Use
the ``trial(1)`` command, distributed as part of Twisted::

  $ trial comet
  [...]
  -------------------------------------------------------------------------------
  Ran 36 tests in 1.334s

  PASSED (successes=36)

(of course, more tests may well have been added since this was written!).

Terminology
-----------

The VTP system defines three types of nodes -- Author, Broker and Subscriber
-- and two types of connection -- Author to Broker and Broker to Subscriber.
Comet has the capabilty to act in all of these roles.

Usage
-----
Publishing VOEvents
===================

The ``comet-sendvo`` command acts fulfils the Author role in an Author to
Broker connection. It can read an event to send either from a file or from
standard input, and accepts command line options specifying the host and port
to send to::

  $ comet-sendvo --help
  Usage: comet-sendvo [options]
  Options:
    -h, --host=    Host to send to. [default: localhost]
    -p, --port=    Port to send to. [default: 8098]
    -f, --file=    Where to read XML text to send (- is stdin). [default: -]
        --version  Display Twisted version and exit.
        --help     Display this help and exit.

The VOEvent Broker
==================

The Comet broker is implemented as a Twisted application, and, as such, is run
using ``twistd(1)``. ``twistd`` is installed as part of Twisted, and provides
support for daemonization, logging, etc: see the man page for more detail.

Comet accepts a few command line options::

  $ twistd comet --help
  Usage: twistd [options] comet [options]
  Options:
    -r, --receive          Listen for TCP connections from authors.
    -b, --broadcast        Re-broadcast VOEvents received.
    -v, --verbose          Increase verbosity.
    -q, --quiet            Decrease verbosity.
        --local-ivo=       [default: ivo://comet.broker/default_ivo]
        --eventdb=         Event database root. [default: /tmp]
        --receive-port=    TCP port for receiving events. [default: 8098]
        --broadcast-port=  TCP port for broadcasting events. [default: 8099]
        --whitelist=       Network to be included in submission whitelist.
                           [default: 0.0.0.0/0]
        --remote=          Remote broadcaster to subscribe to (host[:port]).
        --filter=          XPath filter applied to events broadcast by remote.
        --action=          Add an event handler.
        --cmd=             Spawn external command on event receipt.
        --help             Display this help and exit.
        --version          Display Twisted version and exit.

If the ``--receive`` option is supplied, Comet will fulfil the Broker role in
an Author to Broker connection. In other words, it will listen for TCP
connections from remote authors and accept events for distribution. The TCP
port on which Comet will listen may be specified with the ``--receive-port``
option.

If the ``--broadcast`` option is supplied, Comet will allow Subscribers to
connect and then it will fulfil the Broker role in a Broker to Subscriber
connection with each of the Subscribers.  Any VOEvents received (either by
direct connection from authors, or by subscribing to remote brokers) are
rebroadcast to subscribers. The TCP port on which Comet will allow subscribers
to connect may be specified with the ``--broadcast-port`` option.

If one or more ``--remote`` options are supplied, Comet will subscribe to the
remote host specified and fulfil the Subscriber role in the resulting Broker
to Subscriber connection. If just given a hostname Comet will attempt to
subscribe on port 8099. Optionally, a different port may be specified by
appending it to the hostname, separated by a ``:``.

A single Comet daemon will accept any combination ``--receiver``,
``--broadcast`` and one or more ``--remote`` options and play all of these
roles simultaneously.  If none of ``--receiver``, ``--broadcast`` or
``--remote`` are supplied, there is no work to be done and Comet will exit
immediately.

All modes of operation identify themselves by means of an IVORN: see the
`VOEvent standard <http://www.ivoa.net/Documents/VOEvent/index.html>`_ for
details. You should specify some appropriate IVORN for your site using the
``--local-ivo`` option.

In order to prevent looping on the network (ie, two brokers exchanging the
same event ad infinitum), a database of previously seen event is maintained.
This database is written to the filesystem in the location specified by the
``--eventdb`` option. This database is important: looping would degrade the
quality of the VOEvent network for all users! Note that events persist in the
database for 30 days, after which they are expired to save space. Further,
note that events are compared using checksums, so a single character
difference (eg, an additional space) between otherwise identical events will
cause them to be regarded as distinct.

The Comet receiver will only accept new events for publication from hosts
which have been specified as "whitelisted". Hosts (or, indeed, networks) may
be included in the whitelist using the ``--whitelist`` option. This option
accepts either `CIDR <https://en.wikipedia.org/wiki/CIDR_notation>`_ or
dot-decimal notation including a subnet mask. For example, ``--whitelist
127.0.0.1/32`` and ``--whitelist 127.0.0.1/255.255.255.255`` would both enable
the local host to submit events to the broker. This option may be specified
multiple times.  To accept submissions from any host, specify ``--whitelist
0.0.0.0/0``; this is the default.

When connecting to a remote broker (with ``--remote``), one or more filters
may be specified which limit the events which will be received. These filters
are specified with ``--filter``, in the form of `XPath 1.0
<http://www.w3.org/TR/xpath/>`_ expressions. The broker will evaluate the
expression against each event it processes, and only forward the event to the
subscriber if it produces a non-empty result. For more details see
`Filtering`_, below.

Custom code may be run to perform local processing on an event when it is
received. This is specifed by the ``--action`` option. For more details, see
`Event handlers`_, below.

In addition, received events may be sent to one or more external commands for
processing. These are specified using the ``--cmd`` option. They should accept
the event on standard input and perform whatever processing is required before
exiting. The standard output and error from the external process is ignored.
If it returns a value other than 0, it will be logged as a failure. Note that
external commands are run in a separate thread, so will not block the
subscriber from processing new events; however, the user is nevertheless
responsible for ensuring that they terminate in a timely fashion.

The amount of information Comet writes to its log may be adjusted using the
``--verbose`` and ``--quiet`` options.

Filtering
---------

As the number of events on the VOEvent backbone increases, it is unlikely that
individual subscribers will want to receive or act upon all of them. Comet
therefore implements an *experimental* filtering system which enables
subscribers to express their preferences as to which events to receive.

At any time, the subscriber may send the broker an `authentication response
message
<http://www.ivoa.net/Documents/Notes/VOEventTransport/20090805/NOTE-VOEventTransport-1.1-20090805.html#_Toc237246942>`_.
(Note that in the current implementation no authentication is actually
requred, and the processing of digital signatures is not supported). Within
the ``<Meta />`` section of the authentication packet, one or more XPath
expressions may be supplied in ``filter`` elements with a ``type`` attribute
equal to ``xpath``. For example, the following will select all VOEvent packets
which are not marked as a test::

  <trn:Transport version="1.0" role="authenticate"
    xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
      http://www.telescope-networks.org/schema/Transport-v1.1.xsd">
    <Origin>ivo://origin</Origin>
    <Response>ivo://response</Response>
    <TimeStamp>2012-02-08T21:13:53</TimeStamp>
    <Meta>
      <filter type="xpath">/*[local-name()="VOEvent" and @role!="test"]</filter>
    </Meta>
  </trn:Transport>

The broker will evaluate each filter against each VOEvent packet it processes,
and only forward it to the subscriber if one (or more) of the filters returns
a positive result.

It is worth noting that XPath expressions may return one of four different
types of result: a boolean, a floating point number, a string, or a node-set.
For the purposes of filtering, we regard a positive result as a boolean true,
a non-zero number, a non-empty string, or a non-empty node-set.

When evaluating the XPath expression, no namespaces are defined. In other
words, an expression such as ``//voe::VOEvent`` will not match anything (and
hence the use of ``local-name()`` in the example above).

The filtering capabilities of XPath are quite extensive, and the user is
encouraged to experiment. For example, the names and values of individual
paramters within the VOEvent message can be checked::

  //Param[@name="SC_Lat" and @value>600]

Or messages from particular senders selected::

  //Who[AuthorIVORN="ivo://lofar.transients/"]

Event handlers
--------------

Comet aims to server as a fairly complete and fully-functional broker.
However, it is anticipated that those interested in subscribing to VOEvent
feeds may have many and varied requirements; it is impossible to take account
of all of them. For these users, Comet serves as a template and
development platform, and they are encouraged to develop it further to meet
their needs.

One way in which the Comet's capabilties may be developed is by providing
"event handlers": Python code which is executed when a new event is received.
In order to make use of this facility, the developer should be familiar with
Twisted's `component architecture
<http://twistedmatrix.com/documents/current/core/howto/components.html>`_.
Handlers may then be written to follow Comet's ``comet.icomet.IHandler``
interface, and then installed in the ``comet/plugins`` directory.  A simple
example is provided in ``comet.plugins.eventprinter``.

Each handler must provide a ``name`` attribute. The user may specify the names
of one or more handlers to use on the command line (the ``--action`` command
line argument).

Future plans
------------

Take a look at the `issue tracker
<https://github.com/jdswinbank/Comet/issues>`_.

Final words
-----------

Comet was developed by `John Swinbank <mailto:swinbank@transientskp.org>`_ as
part of the `LOFAR <http://www.lofar.org/>`_ `Transients Key Project
<http://www.transientskp.org/>`_. Comments and corrections welcome.

See also the `Dakota VOEvent Tools <http://voevent.dc3.com/>`_ for an
alternative high-quality VOEvent distribution system.
