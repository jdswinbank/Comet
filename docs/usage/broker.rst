Broker
======

The Broker is the part of Comet which receives messages from authors and
distributes them to subscribers. It can also subscribe to other brokers and
act upon events received.

The Comet Execution Model
-------------------------

The Comet Broker runs as a single Python process which interfaces with the
outside world in three different ways:

- As an “Event Receiver”, it accepts VOEvent submissions from authors;
- As an “Event Broadcaster”, it distributes VOEvents to subscribers;
- As an “Event Subscriber”, it listens to streams of events from upstream
  brokers.

Multiple instances of each of these major modes may be used simultaneously.
That is, a single Comet instance can receive events from authors on multiple
distinct interfaces (TCP ports, Unix domain sockets, etc); can accept
subscription requests from subscribers on multiple interfaces; and can
subscribe to multiple upstream brokers.

In addition, Comet can process the events it receives through a set of
“handlers” which can perform arbitrary actions based on the event contents.

It's worth noting that Comet maintains a single internal database of events,
and handles every event received in the same way regardless of its source.
That means that every event received, whether by direct submission from an
author or by subscribing to an upstream broker, is processed through the same
set of event handlers, and is rebroadcast to all subscribers (modulo their
individual :ref:`filtering <Filtering>` settings). It is not possible to
configure different event handlers or broadcast policies based on their
source.

Running Comet
-------------
Background Information: Twisted Applications
++++++++++++++++++++++++++++++++++++++++++++

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

Invoking the Broker
+++++++++++++++++++

Specify name of the Twisted application to run after ``twistd`` and its
options. In this case, we run ``comet``, and pass it the ``--help`` option to
provide a brief usage message::

  usage: twistd [options] comet [-h] [--verbose] [--local-ivo LOCAL_IVO]
                                [--eventdb EVENTDB] [--receive [RECEIVE]]
                                [--receive-whitelist [RECEIVE_WHITELIST [RECEIVE_WHITELIST ...]]]
                                [--broadcast [BROADCAST]]
                                [--broadcast-test-interval BROADCAST_TEST_INTERVAL]
                                [--broadcast-whitelist [BROADCAST_WHITELIST [BROADCAST_WHITELIST ...]]]
                                [--subscribe SUBSCRIBE] [--filter FILTERS]
                                [--cmd HANDLERS] [--print-event] [--save-event]
                                [--save-event-directory SAVE_EVENT_DIRECTORY]

  optional arguments:
    -h, --help            show this help message and exit
    --verbose, -v         Increase verbosity (may be specified more than once).

  Standard arguments:
    Global options affecting broker operation.

    --local-ivo LOCAL_IVO
                          IVOA identifier for this system. Required if using
                          --receive or --broadcast.
    --eventdb EVENTDB     Event database root [default=/var/folders/g9/5c5t1myd5
                          4scz1kz39g718b40000gn/T].

  Event Receiver:
    Receive events submitted by remote authors.

    --receive [RECEIVE]   Add an endpoint for receiving events.
    --receive-whitelist [RECEIVE_WHITELIST [RECEIVE_WHITELIST ...]]
                          Networks from which to accept event submissions
                          [default=accept from everywhere].

  Event Broadcaster:
    Broadcast events to remote subscribers.

    --broadcast [BROADCAST]
                          Add an endpoint for broadcasting events.
    --broadcast-test-interval BROADCAST_TEST_INTERVAL
                          Interval between test event broadcasts (seconds)
                          [default=3600].
    --broadcast-whitelist [BROADCAST_WHITELIST [BROADCAST_WHITELIST ...]]
                          Networks from which to accept subscription requests
                          [default=accept from everywhere].

  Event Subscriber:
    Subscribe to event streams from remote brokers.

    --subscribe SUBSCRIBE
                          Add a remote broker to which to subscribe.
    --filter FILTERS      XPath filter to be applied to events received from
                          remote brokers.

  Event Processors:
    Define 'event handlers' which are applied to all events processed by this
    system.

    --cmd HANDLERS        External command to spawn when an event is received.
    --print-event         Enable the print-event plugin.
    --save-event          Enable the save-event plugin.
    --save-event-directory SAVE_EVENT_DIRECTORY
                          Directory in which to save events

When asked to provide ``--help``, the application exits immediately after
printing this message: further configuration is required put Comet to work.

Environment Variables
+++++++++++++++++++++

.. envvar:: COMET_PLUGINPATH

  By default, Comet will search the :file:`comet/plugins` directory in its own
  source tree for :ref:`plugins <Plugins>`. This search path may be augmented
  by setting :envvar:`COMET_PLUGINPATH` in the environment::

    COMET_PLUGINPATH=/path/to/plugins twistd comet ...

Configuration
-------------

All configuration of the Comet broker is performed by specifying command line
options: Comet does not read a configuration file.

.. note::

   At least one ``--receive``, ``--broadcast``, or ``--subscribe`` option is
   required to enable Comet's functionality. If none are supplied, there is no
   work to be done and Comet will exit immediately.

Global Options
++++++++++++++

Global options take effect whichever of the various modes (receiver,
broadcaster, subscriber) are active.

Verbosity
"""""""""

The ``--verbose`` or ``-v`` flag increases the amount of information that
Comet writes to its log. It may be specified more than once; the effects are
cumulative.

Site Identification
"""""""""""""""""""

Comet identifies itself to other systems by means of an *International Virtual
Observatory Identifier* or *IVOID*: see the `IVOA Identifiers Version 2.0
standard <http://www.ivoa.net/documents/IVOAIdentifiers/20160523/index.html>`_
for details.

.. note::

   The `VOEvent standard <http://www.ivoa.net/Documents/VOEvent/index.html>`_
   uses the older term “IVORN” rather than IVOID; Comet prefers the more
   modern usage.

You should specify some appropriate IVOID for your site using the
``--local-ivo`` option.  This is required when operating as a receiver or
broadcaster; it's optional, but will be used if provided, when operating as a
subscriber. IVOIDs take the form ``ivo://${organization}/${name}``; for
example, ``ivo://org.transientskp/comet_broker``.

Event Database Location
"""""""""""""""""""""""

In order to prevent looping on the network (ie, two brokers exchanging the
same event ad infinitum), a database of previously seen event is maintained.
By default, the database is written to a system-dependent default location,
but a specific directory on the filesystem may be specified by the
``--eventdb`` option.  Events which are recorded in the database are not
forwarded by Comet. This is important: looping would degrade the quality of
the VOEvent network for all users! Note that events persist in the database
for 30 days, after which they are expired to save space.

Event Receiver
++++++++++++++

The event receiver is enabled by specifying the ``--receive`` option.

``--receive`` optionally takes an argument which specifies the endpoint on
which to listen for events. This is specified as a `Twisted server endpoint`_.
For example, possible arguments include:

- ``tcp:8098``, to listen on TCP port 8098;
- ``unix:/some/file/name`` to listen to the `Unix domain socket` at path
  :file:`/some/file/name`.

If an integer is provided, it is assumed to correspond to a TCP port on which
to listen.

If no argument is provided to ``--receive``, the receiver will listen on TCP
port 8099 on all network interfaces.

``--receive`` may be specified multiple times, each corresponding to a
different endpoint; Comet will listen for event submissions on all of them
simultaneously.

When acting as an event receiver, Comet will only accept new events for
publication from hosts which have been specified as "whitelisted". Hosts (or,
indeed, networks) may be included in the whitelist using the
``--receive-whitelist`` option. This option accepts either `CIDR`_ or
dot-decimal notation including a subnet mask. For example,
``--receive-whitelist 127.0.0.1/32`` and ``--receive-whitelist
127.0.0.1/255.255.255.255`` both permit the local host to submit events to the
broker. Multiple networks may be specified, separated by spaces. To accept
submissions from any host, specify ``--receive-whitelist 0.0.0.0/0``; this is
the default if no ``--receive-whitelist`` option is supplied.

.. warning::

   The whitelist applies only to events received over the network; it will be
   ignored for connections using Unix domain sockets.

.. _Twisted server endpoint: https://twistedmatrix.com/documents/current/core/howto/endpoints.html
.. _CIDR: https://en.wikipedia.org/wiki/CIDR_notation

Event Broadcaster
+++++++++++++++++

The event broadcaster is enabled by specifying the ``--broadcast`` option.

``--broadcast`` optionally takes an argument which specifies the endpoint on
which to listen for subscribers. This is specified as a `Twisted server
endpoint`_.  For example, possible arguments include:

- ``tcp:8099``, to listen on TCP port 8099;
- ``unix:/some/file/name`` to listen to the `Unix domain socket` at path
  :file:`/some/file/name`.

If an integer is provided, it is assumed to correspond to a TCP port on which
to listen.

If no argument is provided to ``--broadcast``, the broadcaster will listen on
TCP port 8098 on all network interfaces.

``--broadcast`` may be specified multiple times, each corresponding to a
different endpoint; Comet will listen for event submissions on all of them
simultaneously.

When acting as an event receiver, Comet will only accept subscription requests
from hosts which have been specified as "whitelisted". Hosts (or, indeed,
networks) may be included in the whitelist using the ``--broadcast-whitelist``
option. This option accepts either `CIDR`_ or dot-decimal notation including a
subnet mask. For example, ``--broadcast-whitelist 127.0.0.1/32`` and
``--broadcast-whitelist 127.0.0.1/255.255.255.255`` both permit the local host
to submit events to the broker. Multiple networks may be specified, separated
by spaces. To accept subscription requests from any host, specify
``--broadcast-whitelist 0.0.0.0/0``; this is the default if no
``--broadcast-whitelist`` option is supplied.

.. warning::

   The whitelist applies only to events received over the network; it will be
   ignored for connections using Unix domain sockets.

By default, Comet will broadcast a content-free test event to all subscribers
every hour to help with network debugging. The interval between test events
may be configured using the ``--broadcast-test-interval`` option, which
accepts a value in seconds. Set it to ``0`` to disable the test broadcast
completely.

.. _Twisted server endpoint: https://twistedmatrix.com/documents/current/core/howto/endpoints.html
.. _CIDR: https://en.wikipedia.org/wiki/CIDR_notation

Event Subscriber
++++++++++++++++

The event receiver is enabled by specifying the ``--subscribe`` option.

``--subscribe`` requires an argument which specifies the remote broker to
which to connect. This is specified as a `Twisted client endpoint`_.  For
example, possible arguments include:

- ``tcp:hostname:8099``, to make a subscription request over TCP on port 8099
  to the broker with hostname ``hostname``;
- ``unix:/some/file/name`` to make a subscription request over the Unix domain
  socet at path :file:`/some/file/name`.

If the protocol specification is omitted, TCP is assumed; if the port is
omitted, 8099 is assumed.

Optionally, the subscriber may request that the remote broker apply filters to
the event stream, limiting the events which it sends to the client.  These
filters are specified with ``--filter``, in the form of `XPath 1.0
<http://www.w3.org/TR/xpath/>`_ expressions. The broker will evaluate the
expression against each event it processes, and only forward the event to the
subscriber if it produces a non-empty result. For more details see the section
on :ref:`filtering <filtering>`.

.. _Twisted client endpoint: https://twistedmatrix.com/documents/current/core/howto/endpoints.html

Event Processors
++++++++++++++++

The same set of event processors are applied to *all* events received by the
broker, whether they come through direct submission by an author to the Event
Receiver, or by broadcast from an upstream broker to the Event Subscriber.

.. _plugins:

Plugins
"""""""

Custom code may be run to perform arbitrary local processing on an event when
it is received. For more details, see the section on :doc:`event handlers
</handlers>`. A plugin is enabled by giving its name as a command line option
(``--plugin-name``).  Plugins may also take arguments from the command line.
These are given in the form ``--plugin-name-argument=value``.

Comet ships with two plugins which both serve as examples of how to write
event handlers and which may be useful in their own right. The first simply
writes events to Comet's log as they are received. This is the ``print-event``
plugin: enable it by invoking Comet with the ``--print-event`` option.

The second plugin shipped with Comet is ``save-event``, which writes events to
file. It is enabled with the ``--save-event`` option. By default, events are
written to the default working directory (normally the directory in which you
invoked Comet): this may be customized using the ``--save-event-directory=``
option. The filename under which an event is saved is based on its IVOID, but
modified to avoid characters which are awkard to work with on standard
filesystems.

Additional, user-defined, plugins may be added by placing them either in the
:file:`comet/plugins` directory, or in the location specified by
:envvar:`COMET_PLUGINPATH`.

.. _spawn:

Spawning External Commands
""""""""""""""""""""""""""

Similarly, received events may be sent to one or more external commands for
processing. These are specified using the ``--cmd`` option. They should accept
the event on standard input and perform whatever processing is required before
exiting. The standard output and error from the external process will be
written to Comet's log with level ``DEBUG``. If it returns a value other than
``0``, it will be logged as a failure.  Note that external commands are run in
a separate thread, so will not block the subscriber from processing new
events; however, the user is nevertheless responsible for ensuring that they
terminate in a timely fashion.
