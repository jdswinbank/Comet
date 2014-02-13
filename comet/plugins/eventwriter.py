# Comet VOEvent Broker.
# Example event handler: print an event.
# John Swinbank, <swinbank@trtransientskp.org>, 2012.

import os
import lxml.etree as ElementTree
from zope.interface import implementer
from twisted.plugin import IPlugin
from ..icomet import IHandler, IHasOptions
from ..utility import log

# Event handlers must implement IPlugin and IHandler.
# Implementing IHasOptions enables us to use command line options.
@implementer(IPlugin, IHandler, IHasOptions)
class EventWriter(object):
    # Simple example of an event handler plugin. This saves the events to
    # disk.

    # The name attribute enables the user to specify plugins they want on the
    # command line.
    name = "save-event"

    def __init__(self):
        self.directory = os.getcwd()

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):
        """
        Save an event to disk.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        filename = "".join(x for x in event.attrib['ivorn'] if x.isalnum())
        log.debug("Writing to %s" %filename)
        with open(os.path.join(self.directory, filename), 'w') as f:
            f.write(ElementTree.tostring(event.element))

    def get_options(self):
        return [('directory', self.directory, 'Target directory')]

    def set_option(self, name, value):
        if name == "directory":
            self.directory = value

# This instance of the handler is what actually constitutes our plugin.
save_event = EventWriter()
