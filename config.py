# VOEvent system configuration.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# This is quick and dirty!
RECEIVER_LISTEN_ON    = "tcp:8099"
PUBLISHER_LISTEN_ON   = "tcp:8100"
SUBSCRIBER_CONNECT_TO = "tcp:host=localhost:port=8100"
SENDER_CONNECT_TO     = "tcp:host=localhost:port=8099"
LOCAL_IVO             = "ivo://lofar/transients"
