# Comet VOEvent Broker.
# Example event handler: write an event to file.

import os
import string
from contextlib import contextmanager

from zope.interface import implementer
from twisted.plugin import IPlugin
from twisted.python import lockfile

from comet.icomet import IHandler, IHasOptions
import comet.log as log

def string_to_filename(input_string):
    # Strip weird, confusing or special characters from input_string so that
    # we can safely use it as a filename.
    # Replace "/" and "\" with "_" for readability.
    # Allow ".", but not as the first character.
    if input_string[0] == ".":
        input_string = input_string[1:]
    return "".join(x for x in input_string.replace("/", "_").replace("\\", "_")
        if x in string.digits + string.ascii_letters + "_."
    )

@contextmanager
def event_file(ivoid, dirname=None):
    # Return a file object into which we can write an event.
    # If a directory is specified, write into that; otherwise, use the cwd.
    # We use a lock to ensure we don't clobber other files with the same name.
    if not dirname:
        dirname=os.getcwd()
    fname = os.path.join(dirname, string_to_filename(ivoid))
    lock = lockfile.FilesystemLock(string_to_filename(ivoid) + "-lock")
    lock.lock()
    try:
        while os.path.exists(fname):
            fname += "."
        with open(fname, 'w') as f:
            yield f
    finally:
        lock.unlock()

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
        with event_file(event.element.attrib['ivorn'], self.directory) as f:
            log.debug("Writing to %s" % (f.name,))
            f.write(event.raw_bytes.decode(event.encoding))

    def get_options(self):
        return [('directory', self.directory, 'Target directory')]

    def set_option(self, name, value):
        if name == "directory":
            self.directory = value

# This instance of the handler is what actually constitutes our plugin.
save_event = EventWriter()
