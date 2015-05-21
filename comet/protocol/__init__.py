# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@princeton.edu>, 2011-15.

"""
Implements the VOEvent Transport Protocol; see
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

All messages consist of a 4-byte network ordered payload size followed by the
payload data. Twisted's Int32StringReceiver handles this for us automatically.

There are four different VOEvent protocols to implement:

* VOEventBroadcaster

    * Listens for connections from subscribers, sends VOEvent messages.

* VOEventReceiver

    * Receives messages from VOEventSender.

* VOEventSender

    * Connects to VOEventReceiver and publishes a new message.

* VOEventSubscriber

    * Opens connection to remote broker, receives VOEvent messages.

To implement the broker, we need the Subscriber, Broadcaster & Receiver, but not
the Sender. All four are provided here for completeness.
"""
from broadcaster import VOEventBroadcaster, VOEventBroadcasterFactory
from receiver import VOEventReceiver, VOEventReceiverFactory
from sender import VOEventSender, VOEventSenderFactory
from subscriber import VOEventSubscriber, VOEventSubscriberFactory
