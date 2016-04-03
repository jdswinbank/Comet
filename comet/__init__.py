__description__ = "VOEvent Broker"
__url__ = "http://comet.transientskp.org/"
__author__ = "John Swinbank"
__contact__ = "swinbank@princeton.edu"
__version__ = "2.1.0-pre"

import sys

if sys.version_info.major <= 2:
    BINARY_TYPE = str
else:
    BINARY_TYPE = bytes
