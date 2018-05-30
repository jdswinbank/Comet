# Comet VOEvent Broker.
# Utilities in support of broker tests.

import shutil
import tempfile
import textwrap
from contextlib import contextmanager
from functools import partial
import lxml.etree as etree
from comet.protocol.messages import authenticateresponse

# All dummy event text should be RAW BYTES, as received over the network.

DUMMY_EVENT_IVOID = u"ivo://comet.broker/test#1234567890".encode('UTF-8')
DUMMY_SERVICE_IVOID = u"ivo://comet.broker/test".encode('UTF-8')

DUMMY_IAMALIVE = u"""
    <?xml version=\'1.0\' encoding=\'UTF-8\'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="iamalive">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVOID.decode(),)
DUMMY_IAMALIVE = textwrap.dedent(DUMMY_IAMALIVE).strip().encode('UTF-8')

DUMMY_AUTHENTICATE = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="authenticate">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVOID.decode(),)
DUMMY_AUTHENTICATE = textwrap.dedent(DUMMY_AUTHENTICATE).strip().encode('UTF-8')

DUMMY_VOEVENT = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <voe:VOEvent xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0
            http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
        version="2.0" role="test" ivorn="%s">
        <Who>
            <AuthorIVORN>%s</AuthorIVORN>
            <Date>2012-01-01T00:00:00</Date>
        </Who>
    </voe:VOEvent>
""" % (DUMMY_EVENT_IVOID.decode(), DUMMY_SERVICE_IVOID.decode())
DUMMY_VOEVENT = textwrap.dedent(DUMMY_VOEVENT).strip().encode('UTF-8')

DUMMY_ACK = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="ack">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode())
DUMMY_ACK = textwrap.dedent(DUMMY_ACK).strip().encode('UTF-8')

DUMMY_NAK = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="nak">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode())
DUMMY_NAK = textwrap.dedent(DUMMY_NAK).strip().encode('UTF-8')

DUMMY_AUTHENTICATE_RESPONSE_LEGACY = u"""
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="authenticate">
        <Origin>%s</Origin>
        <Response>%s</Response>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
        <Meta>
            <filter type="xpath">%s</filter>
        </Meta>
    </trn:Transport>
""" % (DUMMY_SERVICE_IVOID.decode(), DUMMY_SERVICE_IVOID.decode(), "%s")
DUMMY_AUTHENTICATE_RESPONSE_LEGACY = textwrap.dedent(
    DUMMY_AUTHENTICATE_RESPONSE_LEGACY
).strip().encode('UTF-8')

DUMMY_AUTHENTICATE_RESPONSE = partial(
    authenticateresponse, DUMMY_SERVICE_IVOID, DUMMY_SERVICE_IVOID
)

class DummyEvent(object):
    def __init__(self, ivoid=DUMMY_EVENT_IVOID):
        self.attrib = {'ivorn': ivoid}
        self.raw_bytes = DUMMY_VOEVENT.replace(DUMMY_EVENT_IVOID, ivoid)
        self.element = etree.fromstring(self.raw_bytes)

class DummyLogObserver(object):
    def __init__(self):
        self.messages = []

    def __call__(self, logentry):
        self.messages.append(logentry['message'])

@contextmanager
def temp_dir():
    """
    Provide a context with a temporary directory. Clean it up when done.
    """
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)
