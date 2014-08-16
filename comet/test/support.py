import textwrap
from functools import partial
import lxml.etree as etree
from comet.tcp.messages import authenticateresponse

DUMMY_EVENT_IVORN = "ivo://comet.broker/test#1234567890"
DUMMY_SERVICE_IVORN = "ivo://comet.broker/test"

DUMMY_IAMALIVE = """
    <?xml version=\'1.0\' encoding=\'UTF-8\'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="iamalive">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVORN,)
DUMMY_IAMALIVE = textwrap.dedent(DUMMY_IAMALIVE).strip()

DUMMY_AUTHENTICATE = """
    <?xml version='1.0' encoding='UTF-8'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="authenticate">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00Z</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVORN,)
DUMMY_AUTHENTICATE = textwrap.dedent(DUMMY_AUTHENTICATE).strip()

DUMMY_VOEVENT = """
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
""" % (DUMMY_EVENT_IVORN, DUMMY_SERVICE_IVORN)
DUMMY_VOEVENT = textwrap.dedent(DUMMY_VOEVENT).strip()

DUMMY_ACK = """
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
""" % (DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN)
DUMMY_ACK = textwrap.dedent(DUMMY_ACK).strip()

DUMMY_NAK = """
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
""" % (DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN)
DUMMY_NAK = textwrap.dedent(DUMMY_NAK).strip()

DUMMY_AUTHENTICATE_RESPONSE_LEGACY = """
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
""" % (DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN, "%s")
DUMMY_AUTHENTICATE_RESPONSE_LEGACY = textwrap.dedent(DUMMY_AUTHENTICATE_RESPONSE_LEGACY).strip()

DUMMY_AUTHENTICATE_RESPONSE = partial(
    authenticateresponse, DUMMY_SERVICE_IVORN, DUMMY_SERVICE_IVORN
)

class DummyEvent(object):
    def __init__(self, ivorn=DUMMY_EVENT_IVORN):
        self.attrib = {'ivorn': ivorn}
        self.text = DUMMY_VOEVENT.replace(DUMMY_EVENT_IVORN, ivorn)
        self.element = etree.fromstring(self.text)
