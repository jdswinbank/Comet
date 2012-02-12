=====
Comet
=====
----------------
A VOEvent Broker
----------------

Comet is designed to serve as a development testbed for rapid prototyping of
and experimentation with VOEvent transport systems. Currently, it partially
implements the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_.

Comet provides three compoents:

- A tool to publish VOEvent messages to a remote broker;
- A subscriber, which will connect to a remote broker, subscribe to a stream
  of VOEvents, and collect them for processing locally;
- A broker, which will subscribe to one or more remote brokers and listen for
  events being published by direct TCP connection, forwarding the results to
  its own subscribers

Requirements
------------

Comet is developed targeting Python 2.6 and 2.7. It depends upon `Twisted
<http://twistedmatrix.com/>`_ (versions >= 11), `lxml <http://lxml.de/>`_
(versions >= 2.3) and `ipaddr-py <https://code.google.com/p/ipaddr-py/>`_.

Installation
------------

A `distutils <http://docs.python.org/library/distutils.html>`_ ``setup.py``
script is included. To install in your system-default location, simply run::

  $ python setup.py install

See also::

  $ python setup.py --help

for more details.

Usage
-----
Publishing VOEvents
===================

The ``comet-sendvo`` command is used to publish an event to a remote broker.
It can read the event to send either from a file or from standard input, and
accepts command line options specifying the host and port to send to::

  $ comet-sendvo --help
  Usage: comet-sendvo [options]
  Options:
    -h, --host=    Host to send to. [default: localhost]
    -p, --port=    Port to send to. [default: 8098]
    -f, --file=    Where to read XML text to send. [default: -]
        --version  Display Twisted version and exit.
        --help     Display this help and exit.

Subscribing to a VOEvent stream
===============================

The subscriber is implemented as a Twisted application, and, as such, is run
using ``twistd(1)``. ``twistd`` is installed as part of Twisted, and provides
support for daemonization, logging, etc: see the man page for more detail.

The subscriber accepts a few command line options::

  Usage: twistd [options] subscriber [options]
  Options:
        --local-ivo=  [default: ivo://comet.broker/default_ivo]
    -h, --host=       Host to subscribe to. [default: localhost]
    -p, --port=       Port to subscribe to. [default: 8099]
    -f, --filter=     XPath expression.
        --action=     Add an event handler.
        --version     Display Twisted version and exit.
        --help        Display this help and exit.

A simple invocation might thus look like::

  $ twistd -n subscriber --local-ivo=ivo://comet.test/test

You should specify some sensible IVORN which your subscriber will use to
identify itself: see the `VOEvent standard
<http://www.ivoa.net/Documents/VOEvent/index.html>`_ for details.

The ``-n (--nodaemon)`` flag instructs ``twistd`` to run in the foreground
rather than daemonizing.

By default, when a new event is received, it will be displayed in the
subscriber's log (the location of which may be customized through the
``twistd`` options). It is also possible for the end user to provide their own
"handlers" which are used to execute arbitrary code in response to a new
event: see `Event handlers`_, below.

It is also possible to specify one or more filters, in the form of `XPath 1.0
<http://www.w3.org/TR/xpath/>`_ expressions. The broker will evaluate the
expression against each event it processes, and only forward the event to the
subscriber if it produces a non-empty result. For more details see
`Filtering`_, below.

Running a broker
================

The broker is also a Twisted application controlled through ``twistd``; please
see the notes descrbing the subscriber for a brief introduction. It also
accepts a set of command line options::

  $ twistd broker --help
  Usage: twistd [options] broker [options]
  Options:
        --local-ivo=        [default: ivo://comet.broker/default_ivo]
    -r, --receiver-port=    TCP port for receiving events. [default: 8098]
    -p, --subscriber-port=  TCP port for publishing events. [default: 8099]
    -i, --ivorndb=          IVORN database root. [default: /tmp]
        --whitelist=        Network to be included in submission whitelist (CIDR).
        --remote=           Remote broker to subscribe to (host:port).
        --version           Display Twisted version and exit.
        --help              Display this help and exit.

The broker will listen for publishers (such as ``coment-sendvo``) connecting
on the receiver port specified. Currently, no authentication or filtering of
publishers is performed. Events are only accepted for publication if they are
valid according to the `VOEvent 2.0 schema
<http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd>`_. When an event is
received and accepted, it is broadcast to all the broker's subscribers.

The broker will listen for subscribers (such as the subscriber application
described above) connecting on the subscriber port specified. When the broker
receives and validates a new event, it is distributed to all subscribers.

The broker may subscribe to any number of remote brokers and will
re-broadcast to its subscribers any events it receives. Remote brokers should
be specified on the command line using the ``--remote`` option in the form of
a hostname, followed by a colon, followed by a port number. For example:
``--remote voevent.transientskp.org:8099``. This option may be specified
multiple times.

The broker will only accept new events for publication from hosts which have
been specified as "whitelisted". Hosts (or, indeed, networks) may be included
in the whitelist using the ``--whitelist`` option. This option accepts either
`CIDR <https://en.wikipedia.org/wiki/CIDR_notation>`_ or dot-decimal notation
including a subnet mask. For example, ``--whitelist 127.0.0.1/32`` and
``--whitelist 127.0.0.1/255.255.255.255`` would both enable the local host
to submit events to the broker. This option may be specified multiple times.
To accept submissions from any host, specify ``--whitelist 0.0.0.0/0``.

In order to prevent looping on the network (ie, two brokers exchanging the
same event ad infinitum), a database of previously seen event IVORNs is
maintained. This database is written to the filesystem in the location
specified by the ``-i (--ivorndb)`` option. This database is important:
looping would degrade the quality of the VOEvent network for all users! Note
that the current implementation of the database will grown indefinitely: if
the broker is in a situation where an extremely high volume of VOEvent
messages are expected, the current implementation will not be adequate.

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

Although the ``broker`` aims to serve as a fairly complete and
fully-functional broker, it is anticipated that those interested in
subscribing to VOEvent feeds may have varied and unforeseen requirements. The
``subscriber`` module provided by Comet therefore only serves as a template,
and it is expected that subscribers will wish to develop it further to meet
their needs.

One way in which the ``subscriber``'s capabilties may be developed is by
providing "event handlers": Python code which is executed when a new event is
received. In order to make use of this facility, the developer should be
familiar with Twisted's `component architecture
<http://twistedmatrix.com/documents/current/core/howto/components.html>`_.
Handlers may then be written to follow Comet's ``comet.icomet.IHandler``
interface, and then installed in the ``comet/plugins`` directory.
A simple example is provided in ``comet.plugins.eventprinter``.

Each handler must provide a ``name`` attribute. The user may specify the names
of one or more handlers to use on the command line (the ``--action`` argument
to the ``subscriber``). If no action is specified, all available handlers are
loaded by default.

Future plans
------------

Take a look at the `issue tracker
<https://github.com/jdswinbank/Comet/issues>`_.

Final words
-----------

Comet was developed by `John Swinbank <mailto:swinbank@transientskp.org>`_ as
part of the `LOFAR <http://www.lofar.org/>`_ `Transients Key Project
<http://www.transientskp.org/>`_. Comments and corrections welcome.

Comet is intended priarily as a research system. See the `Dakota VOEvent Tools
<http://voevent.dc3.com/>`_ for a complete, high-quality VOEvent distribution
system.
