import os
import shutil
import tarfile
import tempfile
from StringIO import StringIO
import lxml.etree as etree

from twisted.internet import task
from twisted.trial import unittest
from twisted.test import proto_helpers

from ...test.support import DUMMY_VOEVENT
from ...test.support import DUMMY_SERVICE_IVORN

from ..receiver import SingleReceiver, SingleReceiverFactory
from ..receiver import BulkReceiver, BulkReceiverFactory

class GenericReceiverFactoryTestCase(object):
    factory_type = None
    protocol_type = None

    def setUp(self):
        self.factory = self.factory_type(DUMMY_SERVICE_IVORN)

    def test_protocol(self):
        self.assertEqual(self.factory.protocol, self.protocol_type)

    def test_contents(self):
        self.assertEqual(self.factory.local_ivo, DUMMY_SERVICE_IVORN)
        self.assertFalse(self.factory.validators) # Should be empty
        self.assertFalse(self.factory.handlers)   # Should be empty


class SingleReceiverFactoryTestCase(GenericReceiverFactoryTestCase, unittest.TestCase):
    factory_type = SingleReceiverFactory
    protocol_type = SingleReceiver


class BulkReceiverFactoryTestCase(GenericReceiverFactoryTestCase, unittest.TestCase):
    factory_type = BulkReceiverFactory
    protocol_type = BulkReceiver


class SingleReceiverTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = SingleReceiverFactory(DUMMY_SERVICE_IVORN)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_receive_unparsable(self):
        # An unparsable message should generate no response and the
        # transport should disconnect.
        self.tr.clear()
        unparsable = "This is not parsable"
        self.assertRaises(etree.ParseError, etree.fromstring, unparsable)
        self.proto.stringReceived(unparsable)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, False)

    def test_receive_incomprehensible(self):
        # An incomprehensible message should generate no response and the
        # transport should disconnect.
        self.tr.clear()
        incomprehensible = "<xml/>"
        etree.fromstring(incomprehensible) # Should not raise an error
        self.proto.stringReceived(incomprehensible)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, False)

    def test_receive_voevent(self):
        self.tr.clear()
        self.proto.stringReceived(DUMMY_VOEVENT)
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "ack"
        )
        self.assertEqual(self.tr.connected, False)

    def test_receive_voevent_invalid(self):
        def fail(event):
            raise Exception("Invalid")
        self.factory.validators.append(fail)
        self.tr.clear()
        self.proto.stringReceived(DUMMY_VOEVENT)
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "nak"
        )
        self.assertEqual(self.tr.connected, False)

    def test_timeout(self):
        self.clock.advance(self.proto.TIMEOUT)
        self.assertEqual(self.tr.connected, False)


def create_tar_string(content=[]):
    """
    Create a string representaton of a tarball containing one file for each
    element in the iterable ``content``.
    """
    buf = StringIO()
    tf = tarfile.open(fileobj=buf, mode='w')
    tempdir = tempfile.mkdtemp()
    try:
        for i, data in enumerate(content):
            filename = os.path.join(tempdir, str(i))
            with open(filename, 'w') as f:
                f.write(DUMMY_VOEVENT)
            tf.add(filename)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)
    tf.close()
    buf.seek(0)
    return buf.read()


class BulkReceiverTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = BulkReceiverFactory(DUMMY_SERVICE_IVORN)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.clock = task.Clock()
        self.proto.callLater = self.clock.callLater
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.proto.makeConnection(self.tr)
        self.tr.protocol = self.proto

    def test_receive_junk(self):
        # If we receive a string that does not look like a tarball, we send
        # no response and simply disconnect the transport.
        self.tr.clear()
        junk = StringIO("This is not a tarball")
        self.assertRaises(tarfile.ReadError, tarfile.open, fileobj=junk)
        self.proto.stringReceived(junk)
        self.assertEqual(self.tr.value(), "")
        self.assertEqual(self.tr.connected, False)

    def test_receive_valid(self):
        # If we receive a string containing a tarball that contains a valid
        # VOEvent, we should send an ack and disconnect the transport.
        self.tr.clear()
        self.proto.stringReceived(create_tar_string([DUMMY_VOEVENT]))
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "ack"
        )
        self.assertEqual(self.tr.connected, False)

    def test_receive_invalid(self):
        # If we receive a string containing a tarball that contains an invalid
        # VOEvent, we should send a nak and disconnect the transport.
        def fail(event):
            raise Exception("Invalid")
        self.factory.validators.append(fail)
        self.tr.clear()
        self.proto.stringReceived(create_tar_string([DUMMY_VOEVENT]))
        self.assertEqual(
            etree.fromstring(self.tr.value()[4:]).attrib['role'],
            "nak"
        )
        self.assertEqual(self.tr.connected, False)

    def test_timeout(self):
        self.clock.advance(self.proto.TIMEOUT)
        self.assertEqual(self.tr.connected, False)
