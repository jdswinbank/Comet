import os

from twisted.trial import unittest

from ...icomet import IValidator
from ...utility.xml import xml_document
from ..signature import CheckSignature

from ...test.support import DUMMY_VOEVENT
from ...test.gpg import GPGTestSupport
from ...tcp.test.test_voeventreceiver import VOEventReceiverTestCaseBase

class ValidEvent(object):
    def valid_signature(self):
        return True

class InvalidEvent(object):
    def valid_signature(self):
        return False

class CheckSignatureTestCase(unittest.TestCase):
    def setUp(self):
        self.validator = CheckSignature()

    def test_valid(self):
        self.assertTrue(self.validator(ValidEvent()))

    def test_invalid(self):
        self.assertTrue(self.validator(InvalidEvent()))

    def test_interface(self):
        self.assertTrue(IValidator.providedBy(self.validator))

class CheckSignatureValidatorTestCase(VOEventReceiverTestCaseBase, GPGTestSupport):
    def setUp(self):
        VOEventReceiverTestCaseBase.setUp(self)
        GPGTestSupport.setUp(self)

    def test_receive_voevent_unsigned(self):
        # Unsigned events should be rejected
        self.factory.validators = [CheckSignature()]
        self.tr.clear()
        d = self.proto.stringReceived(DUMMY_VOEVENT)
        d.addCallback(self._sent_nak)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_voevent_signed_untrusted(self):
        # Event with untrusted sig should be rejected
        self.factory.validators = [CheckSignature()]
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_untrusted(doc)
        d = self.proto.stringReceived(doc.text)
        d.addCallback(self._sent_nak)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_voevent_signed_trusted(self):
        # Event with trusted sig should be accepted
        self.factory.validators = [CheckSignature()]
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_trusted(doc)
        d = self.proto.stringReceived(doc.text)
        d.addCallback(self._sent_ack)
        d.addCallback(self._transport_disconnected)
        return d

    def test_receive_voevent_signed_invalid(self):
        # Event with invalid sig should be rejected
        self.factory.validators = [CheckSignature()]
        doc = xml_document(DUMMY_VOEVENT)
        doc = self._sign_trusted(doc)
        d = self.proto.stringReceived(
            doc.text.replace("1234567890", "0987654321")
        ) # Change value of IVORN within signed text
        d.addCallback(self._sent_nak)
        d.addCallback(self._transport_disconnected)
        return d
