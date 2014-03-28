#!/usr/bin/env python

# VOEvent sender.
# John Swinbank, <swinbank@transientskp.org>.

# Python standard library
import sys
import threading
import random
import datetime

# Twisted
from twisted.python.log import startLogging
from twisted.python import usage
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.defer import DeferredSemaphore
from twisted.internet.defer import DeferredLock
from twisted.internet.task import LoopingCall

# VOEvent transport protocol
from comet.tcp.protocol import VOEventSenderFactory

# Encapsulation of event
#from comet.utility.xml import xml_document
#import lxml.etree as ElementTree

from comet.utility import log
from comet.utility.voevent import broker_test_message
from comet.utility.xml import xml_document

class LatencyOptions(usage.Options):
    optParameters = [
        ["interval", None, 0.3, "Interval between events.", float]
    ]

class ThroughputOptions(usage.Options):
    optParameters = [
        ["num-events", None, 10000,"Number of events to send.", int]
    ]

class Options(usage.Options):
    optParameters = [
        ["host", "h", "localhost", "Host to send to."],
        ["port", "p", 8098, "Port to send to.", int],
        ["ivorn", None, "ivo://comet.broker/test", "IVORN."],
        ["connections", None, 1, "Max no. simultaneous connections.", int]
    ]

    subCommands = [['latency', None, LatencyOptions, "Measure latency"],
                   ['throughput', None, ThroughputOptions, "Measure throughput"]]

class PooledVOEventSenderFactory(VOEventSenderFactory):
    def __init__(self, event, pool):
        VOEventSenderFactory.__init__(self, event)
        self.pool = pool

    def clientConnectionLost(self, connector, reason):
        log.info(reason)
        if not self.ack:
            log.info("Sending failed")
            self.pool.failed()
        else:
            self.pool.sent()

    def clientConnectionFailed(self, connector, reason):
        log.info(reason)
        log.info("Connection failed")
        self.pool.failed()


class ConnectionPool(object):
    def __init__(self, host, port, max_connections=1, stop_when_done=False):
        self.lock = threading.Lock()
        self.max_connections = max_connections
        self.connections = 0
        self._failed = 0
        self._sent = 0
        self.queue = []
        self.host = host
        self.port = port
        self.stop_when_done=stop_when_done

    def enqueue(self, message):
        with self.lock:
            self.queue.append(message)
        self._create_connection()

    def _create_connection(self):
        with self.lock:
            if self.queue and self.connections < self.max_connections:
                message = self.queue.pop(0)
                factory = PooledVOEventSenderFactory(message, pool)
                reactor.connectTCP(self.host, self.port, factory)
                self.connections += 1
            elif not self.queue and self.connections == 0:
                print "Nothing to do."
                self.print_status()
                if self.stop_when_done:
                    reactor.stop()

    def failed(self):
        with self.lock:
            self._failed += 1
        self.expire_connection()

    def sent(self):
        with self.lock:
            self._sent += 1
        self.expire_connection()

    def expire_connection(self):
        with self.lock:
            self.connections -= 1
        self._create_connection()

    def print_status(self):
        log.info("%d open connections; %d/%d/%d messages queued/sent/failed" % (self.connections, len(self.queue), self._sent, self._failed))


if __name__ == "__main__":
    config = Options()
    config.parseOptions()

    startLogging(sys.stdout)
    log.LEVEL = log.Levels.DEBUG


    if config.subCommand == "latency":
        pool = ConnectionPool(config['host'], config['port'], config['connections'], False)
        loop = LoopingCall(
            lambda pool, ivorn: pool.enqueue(broker_test_message(ivorn)),
            pool, config['ivorn']
        )
        loop.start(config.subOptions['interval'])

    elif config.subCommand == "throughput":
        pool = ConnectionPool(config['host'], config['port'], config['connections'], True)
        for i in xrange(config.subOptions['num-events']):
            pool.enqueue(broker_test_message(config['ivorn']))

    # Print the status of the pool every 5 seconds.
    ploop = LoopingCall(pool.print_status)
    ploop.start(5)

    start_time = datetime.datetime.now()
    reactor.run()
    stop_time = datetime.datetime.now()
    print "Total reactor running time: %fs" % ((stop_time - start_time).total_seconds(),)
