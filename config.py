# VOEvent system configuration.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# This is quick and dirty!
RECEIVER_LISTEN_ON    = "tcp:8099"
PUBLISHER_LISTEN_ON   = "tcp:8100"
SENDER_CONNECT_TO     = "tcp:host=localhost:port=8099"
SUBSCRIBER_HOST       = "localhost"
SUBSCRIBER_PORT       = 8100
BROKER_SUBSCRIBE_TO   = [("voevent.dc3.com", 8099)]
LOCAL_IVO             = "ivo://lofar/transients"
IVORN_DB_ROOT         = "/tmp"
