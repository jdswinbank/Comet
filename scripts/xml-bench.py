#!/usr/bin/env python

# XML Processing Benchmarking Tool.
#
# Tests to investigate the performance of the XML processing steps that Comet
# performs on each VOEvent received. Specifically, we:
#
# 1. Parse the event text into the appropriate internal data structure,
#    verifying correctness by retrieving the "version" attribute from the XML;
# 2. Verify the event for compliance against the VOEvent 2.0 schema;
# 3. Check the event against a series of XPath queries.
#
# We perform all these checks against an archive of thousands of VTP harvested
# from the VTP "backbone".

import os
import timeit
import glob
from textwrap import dedent
from twisted.python import usage
import lxml.etree as etree

import comet
from comet.utility.voevent import broker_test_message
from comet.utility.event_db import Event_DB
from comet.utility.xml import xml_document

class Options(usage.Options):
    optParameters = [
        ["archive", None, None, "Location of archived events", str],
        ["schema", None, os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd"), "Path to XML schema", str]
    ]

    def postOptions(self):
        if not self["archive"] or not os.path.exists(self["archive"]):
            raise usage.UsageError, "Event archive not found"
        paths = glob.glob(os.path.join(self["archive"], "*"))
        self["event_list"] = [open(path, 'r').read() for path in paths]

def run_bmark(bmark, setup):
    return timeit.Timer(bmark, setup=setup).repeat(10, 1)

def time_event_parse():
    bmark = dedent("""\
    for event in config["event_list"]:
        assert(xml_document(event).get("version") == "2.0")
    """)
    setup = dedent("""\
    from __main__ import xml_document, config
    """)
    return run_bmark(bmark, setup)


def time_schema_check():
    bmark = dedent("""\
    valid = [schema(ev.element) for ev in event_list]
    """)

    setup = dedent("""\
    from __main__ import config, etree, xml_document
    schema = etree.XMLSchema(etree.parse(config["schema"]))
    event_list = [xml_document(event) for event in config["event_list"]]
    """)
    return run_bmark(bmark, setup)


def time_xpath(expression):
    bmark = dedent("""\
    hits = [True if xpath(ev.element) else False for ev in event_list]
    """)

    setup = dedent("""\
    from __main__ import etree, config, xml_document
    xpath = etree.XPath(\"\"\"%s\"\"\")
    event_list = [xml_document(event) for event in config["event_list"]]
    """ % (expression,))
    return run_bmark(bmark, setup)

def print_event_stats(event_list):
    lengths = [len(ev) for ev in event_list]
    print "Processing %d events:" % (len(lengths),)
    print "     Min length: %d characters" % (min(lengths),)
    print "     Max length: %d characters" % (max(lengths),)
    print "    Mean length: %d characters" % (sum(lengths) / len(lengths),)
    print "  Median length: %d characters" % (len(sorted(event_list)[len(event_list)/2]),)

if __name__ == "__main__":
    config = Options()
    config.parseOptions()

    print_event_stats(config["event_list"])

    n_events = len(config["event_list"])
    print "Time to parse one event: %f s." % (min(time_event_parse()) / n_events)
    print "Time to check one event against schema: %f s." % (min(time_schema_check()) / n_events)

    print "Time to evaluate one event against XPath expressions: "
    xpath_text = """//Who/Author[shortName="VO-GCN"]"""
    print "  %s : %f s." % (xpath_text, min(time_xpath(xpath_text)) / n_events)

    xpath_text = """//How[contains(Description, "Swift")]"""
    print "  %s : %f s." % (xpath_text, min(time_xpath(xpath_text)) / n_events)

    xpath_text = ("""//Param[@name="Sun_Distance" and @value>40]""")
    print "  %s : %f s." % (xpath_text, min(time_xpath(xpath_text)) / n_events)

    xpath_text = dedent("""\
        //How[contains(Description, "Swift")] or
             ( //Param[@name="Sun_Distance" and @value>40]
              and //Who/Author[shortName="VO-GCN"])""")
    print "  %s : %f s." % (xpath_text, min(time_xpath(xpath_text)) / n_events)
