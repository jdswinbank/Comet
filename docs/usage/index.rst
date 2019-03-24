Usage
=====

The VTP system defines three types of nodes—Author, Broker and
Subscriber—and two types of conenction—Author to Broker and Broker to
Subscriber. Comet has the capability to act in all of these roles. To do so,
it provides two different tools.

``comet-sendvo`` provides the capability of of publishing a VOEvent packet to
a remote broker. In other words, ``comet-sendvo`` assumes the role of Author
in the above terminology, connects to a remote Broker, and delivers an event
to it. The user invoking Comet in this mode is, of course, responsible for
actually providing the event text to be sent.

The second tool is the Comet broker itself. This runs as a background process
(or “daemon”), and can:

* Accept submissions from Authors (such as ``comet-sendvo``);
* Subscribe to streams of events from one or more remote Brokers;
* Distribute events received (whether by direct author submission or by
  subscription) to its own subscribers;
* Perform arbitrary actions upon events received.

The following pages provide detailed information on using the ``comet-sendvo``
event publisher and the Comet broker.

.. toctree::

   publisher
   broker
