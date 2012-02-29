import textwrap

DUMMY_EVENT_IVORN = "ivo://comet.broker/test#1234567890"
DUMMY_SERVICE_IVORN = "ivo://comet.broker/test"

class DummyEvent(object):
    attrib = {'ivorn': DUMMY_EVENT_IVORN}
    text = "Dummy Text"

DUMMY_IAMALIVE = """
    <?xml version=\'1.0\' encoding=\'UTF-8\'?>
    <trn:Transport xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
            http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
        version="1.0" role="iamalive">
        <Origin>%s</Origin>
        <TimeStamp>2012-01-01T00:00:00</TimeStamp>
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
        <TimeStamp>2012-02-29T16:49:17</TimeStamp>
    </trn:Transport>
""" % (DUMMY_EVENT_IVORN,)
DUMMY_AUTHENTICATE = textwrap.dedent(DUMMY_AUTHENTICATE).strip()
