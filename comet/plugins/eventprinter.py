# Comet VOEvent Broker.
# Example event handler: print an event.
# John Swinbank, <swinbank@trtransientskp.org>, 2012.

import lxml.etree as ElementTree
from zope.interface import implementer
from twisted.plugin import IPlugin
from ..icomet import IHandler

# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventPrinter(object):
    # Simple example of an event handler plugin. This simply prints the
    # received event to standard output.

    # The name attribute enables the user to specify plugins they want on the
    # command line.
    name = "print-event"

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):
        """
        Print an event to standard output.
        """
        print ElementTree.tostring(event.element)

# This instance of the handler is what actually constitutes our plugin.
print_event = EventPrinter()
