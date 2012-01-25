# VOEvent system configuration.
# John Swinbank, <swinbank@transientskp.org>, 2012.

# This is quick and dirty!
RECEIVER_LISTEN_ON    = "tcp:8098"
PUBLISHER_LISTEN_ON   = "tcp:8099"
SENDER_CONNECT_TO     = "tcp:host=localhost:port=8098"
SUBSCRIBER_HOST       = "localhost"
SUBSCRIBER_PORT       = 8099
BROKER_SUBSCRIBE_TO   = [("voevent.dc3.com", 8099)]
LOCAL_IVO             = "ivo://lofar/transients"
IVORN_DB_ROOT         = "/tmp"
