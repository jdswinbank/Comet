================
To Do and Design
================

The broker will be written in Python and make use of the Twisted framework
(until & unless a better alternative is adopted).

The broker must support three types of connection:

1. Broker to Subscriber
2. Broker to Broker
3. Author to Broker

These are defined in the IVOA note. Note that 2 is fundamentally a subset of
1: each broker is just a subscriber as far as other brokers are concerned.

Initially, all VOEvents received from other brokers will be sent to every
subscriber.

Issues to consider include:

Message de-duplication and loop prevention
------------------------------------------

A list of IVORNs of events which have already been processed must be
maintained, and VOEvents should not be relayed if they have already been seen
to prevent looping.

This list must be persistent between broker invocations.

At the moment, it will grow at a modest rate. However, we should be alert to
potential scalability issues in future. What is the smartest way to handle
this? An SQL database?

Is there any value to storing the whole event rather than just the IVORN?

Currently, we use Python's anydbm module for this. I suspect it doesn't scale.

Authentication
--------------

Do we let everybody subscribe?

Ultimately, when we accept author submissions, do we require authentication?
IP whitelisting? Something else?

Quality control
---------------

Is there any value in checking messages for validity?

Applications, Multiservices, etc
--------------------------------

Does all this clever Twisted stuff offer real advantages?

Error handling
--------------

Currently, we have none.
