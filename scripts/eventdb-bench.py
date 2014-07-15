#!/usr/bin/env python

# Event DB benchmarking tool.
#
# Writes batches of events to an event database recording the time to check
# and record an event. Useful both to check basic Event DB performance but
# also to monitor how that changes over time.
#
# Requires Comet to be available for import.

import timeit
import json
from textwrap import dedent
from twisted.python import usage

import comet
from comet.utility.voevent import broker_test_message
from comet.utility.event_db import Event_DB

class Options(usage.Options):
    optParameters = [
        ["num-events", None, 10000000, "Total number of events", int],
        ["chunk-size", None, 10000, "Size of timing interval", int],
        ["eventdb-root", None, "/tmp", "Root directory of Event DB", str]
    ]

# Note that the semantics changed in Comet 1.1.1 such that
# eventdb.check_event() atomically marks an event as seen.
if comet.__version__ < '1.1.1':
    print "Using old-style (pre-1.1.1) Event DB interface."
    BMARK = dedent("""\
    for event in event_list:
        eventdb.check_event(event)
        eventdb.record_event(event)
    """)
else:
    print "Using new-style (1.1.1 and later) Event DB interface."
    BMARK = dedent("""\
    for event in event_list:
        eventdb.check_event(event)
    """)

SETUP = """\
from __main__ import eventdb, broker_test_message
event_list = [broker_test_message("ivo://comet.broker/test") for _ in xrange(%d)]
"""

def benchmark(eventdb, n_events, chunk_size):
    result = []
    for i, time in enumerate(timeit.Timer(BMARK, setup=SETUP % chunk_size).repeat(
                             int(n_events / chunk_size), 1)):
        result.append((i * chunk_size, (i+1) * chunk_size - 1, time/chunk_size))
    return result

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    config = Options()
    config.parseOptions()
    eventdb = Event_DB(config["eventdb-root"])
    save_json(benchmark(eventdb, config["num-events"], config["chunk-size"]), 'out.json')
