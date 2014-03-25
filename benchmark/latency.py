# Comet VOEvent Broker.
# Plugin to measure the latency of received events.
# Assumes that each received event has a "VOEvent/Who/Date" element providing
# a timestamp for the time the event was produced.
# John Swinbank, <swinbank@trtransientskp.org>.

import datetime
import lxml.etree as ElementTree
from zope.interface import implementer
from twisted.plugin import IPlugin
from ..icomet import IHandler
from ..utility import log

# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class LatencyMeasure(object):
    # Simple example of an event handler plugin. This simply prints the
    # received event to standard output.

    # The name attribute enables the user to specify plugins they want on the
    # command line.
    name = "latency"

    def __init__(self):
        self.n_events = 0
        self.max_time = None
        self.min_time = None
        self.mean_time = None

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):
        """
        Print an event to standard output.
        """
        incoming_date = datetime.datetime.strptime(
            event.find("Who").find("Date").text,
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        td = datetime.datetime.now() - incoming_date
        if not self.n_events:
            self.n_events = 1
            self.max_time = self.min_time = self.mean_time = td.total_seconds()
        else:
            self.max_time = max(td.total_seconds(), self.max_time)
            self.min_time = min(td.total_seconds(), self.min_time)
            self.mean_time = (self.mean_time * self.n_events + td.total_seconds()) / (self.n_events + 1)
            self.n_events += 1
        log.info("Received %d events; latency min/max/mean: %f/%f/%f s" % (self.n_events, self.min_time, self.max_time, self.mean_time))

# This instance of the handler is what actually constitutes our plugin.
latency = LatencyMeasure()
