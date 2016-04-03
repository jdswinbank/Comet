# Comet VOEvent Broker.
# Tests for EventPrinter plugin.

import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import lxml.etree as etree

from twisted.trial import unittest
from twisted.plugin import IPlugin

from comet.icomet import IHandler
from comet.plugins.eventprinter import EventPrinter

DUMMY_XML = u'<xml/>'

class DummyEvent(object):
    element = etree.fromstring(DUMMY_XML)

class EventPrinterTestCase(unittest.TestCase):
    def test_interface(self):
        self.assertTrue(IHandler.implementedBy(EventPrinter))
        self.assertTrue(IPlugin.implementedBy(EventPrinter))

    def test_name(self):
        self.assertEqual(EventPrinter.name, "print-event")

    def test_print_event(self):
        event_printer = EventPrinter()
        old_stdout = sys.stdout
        try:
            sys.stdout = StringIO()
            event_printer(DummyEvent())
            sys.stdout.seek(0)
            self.assertEqual(sys.stdout.read().strip(), DUMMY_XML)
        finally:
            sys.stdout = old_stdout
