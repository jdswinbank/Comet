=====
Comet
=====
----------------
A VOEvent Broker
----------------

Comet is designed to serve as a development testbed for rapid prototyping of
and experimentation with VOEvent transport systems. Currently, it partially
implements the `VOEvent Transport Protocol
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_

Comet provides three compoents:

- A tool to publish VOEvent messages to a remote broker;
- A subscriber, which will connect to a remote broker, subscribe to a stream
  of VOEvents, and collect them for processing locally;
- A broker, which will subscribe to one or more remote brokers and listen for
  events being published by direct TCP connection, forwarding the results to
  its own subscribers

Requirements
------------

Comet is developed targeting Python 2.7. It depends upon recent versions of
`Twisted <http://twistedmatrix.com/>`_ and `lxml <http://lxml.de/>`_.

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

``comet-sendvo`` is used to publish an event to a remote broker. It can read
the event to send either from a file or from standard input, and accepts
command line options specifying the host and port to send to::

  $ comet-sendvo --help
  Usage: comet-sendvo [options]
  Options:
    -h, --host=    Host to send to. [default: localhost]
    -p, --port=    Port to send to. [default: 8098]
    -f, --file=    Where to read XML text to send. [default: -]
        --version  Display Twisted version and exit.
        --help     Display this help and exit.
