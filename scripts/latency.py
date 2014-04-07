# Comet VOEvent Broker.
# Plugin to measure the latency of received events.
# Assumes that each received event has a "VOEvent/Who/Date" element providing
# a timestamp for the time the event was produced.

import os
import datetime
import numpy
import lxml.etree as ElementTree
from zope.interface import implementer
from twisted.plugin import IPlugin
from ..icomet import IHandler, IHasOptions
from ..utility import log

@implementer(IPlugin, IHandler, IHasOptions)
class LatencyMeasure(object):
    name = "latency"

    def __init__(self):
        self.latencies = []
        self.output = os.path.join(os.getcwd(), "latencies.log")

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):
        incoming_date = datetime.datetime.strptime(
            event.find("Who").find("Date").text,
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        td = datetime.datetime.now() - incoming_date
        self.latencies.append(td.total_seconds())
        # Write to disk every 10 events
        if not len(self.latencies) % 10:
            with open(self.output, 'a') as output_file:
                output_file.writelines(str(x) + "\n" for x in self.latencies)
                self.latencies = []

    def get_options(self):
        return [('output', self.output, 'Log file')]

    def set_option(self, name, value):
        if name == "output":
            self.output = value

# This instance of the handler is what actually constitutes our plugin.
latency = LatencyMeasure()
