# Comet VOEvent Broker.
# Command-line options for sending events.

import argparse

from comet.utility import BaseOptions

__all__ = ["Options"]

class Options(BaseOptions):
    def _configureParser(self):
        self.parser.add_argument('target', help="Address of receiver to which "
                                                "to send as an endpoint string.")
        self.parser.add_argument('event', type=argparse.FileType('rb'),
                                 help="File containing event text to send; "
                                      "'-' for stdin.")
