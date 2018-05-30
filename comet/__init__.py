__description__ = "VOEvent Broker"
__url__ = "http://comet.transientskp.org/"
__author__ = "John Swinbank"
__contact__ = "john@swinbank.org"
__version__ = "3.0.0"

import sys

if sys.version_info.major <= 2:
    BINARY_TYPE = str
else:
    BINARY_TYPE = bytes
