# Comet VOEvent Broker.
# Master broker service.

# Python standard library
import os.path
from argparse import ArgumentTypeError
from tempfile import gettempdir

# Used for building IP whitelist
from ipaddress import ip_network

# Twisted
from twisted.application.internet import TCPServer
from twisted.application.service import MultiService
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.plugin import getPlugins
from twisted.python import usage

# Comet broker routines
import comet
import comet.log as log
from comet.constants import DEFAULT_SUBMIT_PORT, DEFAULT_SUBSCRIBE_PORT
from comet.service.broadcaster import makeBroadcasterService
from comet.service.subscriber import makeSubscriberService
from comet.service.receiver import makeReceiverService
from comet.utility import Event_DB, BaseOptions, valid_ivoid, valid_xpath
from comet.utility import coerce_to_client_endpoint, coerce_to_server_endpoint
from comet.validator import CheckIVOID, CheckPreviouslySeen, CheckSchema

# Handlers and plugins
import comet.plugins
from comet.icomet import IHandler, IHasOptions
from comet.handler import SpawnCommand, EventRelay

# We only need export the items twistd needs to construct a service.
__all__ = ["makeService", "Options"]

# Constants
MAX_AGE = 30.0 * 24 * 60 * 60  # Forget events after 30 days
PRUNE_INTERVAL = 6 * 60 * 60  # Prune the event db every 6 hours

# By default, we brodcast a test event every BCAST_TEST_INTERVAL seconds.
BCAST_TEST_INTERVAL = 3600


class Options(BaseOptions):
    PROG = "twistd [options] comet"

    def _configureParser(self):
        std_group = self.parser.add_argument_group(
            "Standard arguments", "Global options affecting " "broker operation."
        )
        std_group.add_argument(
            "--local-ivo",
            type=valid_ivoid,
            help="IVOA identifier for this system. "
            "Required if using --receive or --broadcast.",
        )

        # Note that `Event_DB` fails gracefully(ish) if this isn't an
        # appopriate location, so we don't sanity check it here.
        std_group.add_argument(
            "--eventdb",
            default=gettempdir(),
            help="Event database root [default=%(default)s].",
        )

        rcv_group = self.parser.add_argument_group(
            "Event Receiver", "Receive events submitted " "by remote authors."
        )
        rcv_group.add_argument(
            "--receive",
            default=None,
            const=f"tcp:{DEFAULT_SUBMIT_PORT}",
            nargs="?",
            action="append",
            type=lambda ep: coerce_to_server_endpoint(reactor, ep),
            help="Add an endpoint for receiving events.",
        )
        rcv_group.add_argument(
            "--receive-whitelist",
            default=[ip_network("0.0.0.0/0")],
            nargs="*",
            type=ip_network,
            help="Networks from which to accept "
            "event submissions [default=accept from "
            "everywhere].",
        )

        bcast_group = self.parser.add_argument_group(
            "Event Broadcaster", "Broadcast events to " "remote subscribers."
        )
        bcast_group.add_argument(
            "--broadcast",
            default=None,
            const=f"tcp:{DEFAULT_SUBSCRIBE_PORT}",
            nargs="?",
            action="append",
            type=lambda ep: coerce_to_server_endpoint(reactor, ep),
            help="Add an endpoint for broadcasting events.",
        )
        bcast_group.add_argument(
            "--broadcast-test-interval",
            default=BCAST_TEST_INTERVAL,
            type=int,
            help="Interval between test event broadcasts "
            "(seconds) [default=%(default)s].",
        )
        bcast_group.add_argument(
            "--broadcast-whitelist",
            default=[ip_network("0.0.0.0/0")],
            nargs="*",
            type=ip_network,
            help="Networks from which to accept "
            "subscription requests [default=accept "
            "from everywhere].",
        )

        sub_group = self.parser.add_argument_group(
            "Event Subscriber", "Subscribe to event streams" " from remote brokers."
        )
        sub_group.add_argument(
            "--subscribe",
            default=None,
            action="append",
            type=lambda ep: coerce_to_client_endpoint(
                reactor, ep, DEFAULT_SUBSCRIBE_PORT
            ),
            help="Add a remote broker to which " "to subscribe.",
        )
        sub_group.add_argument(
            "--filter",
            default=None,
            action="append",
            dest="filters",
            type=valid_xpath,
            help="XPath filter to be applied to events "
            "received from remote brokers.",
        )

        proc_group = self.parser.add_argument_group(
            "Event Processors",
            "Define 'event handlers' "
            "which are applied to all "
            "events processed by this "
            "system.",
        )
        proc_group.add_argument(
            "--cmd",
            default=None,
            action="append",
            dest="handlers",
            type=SpawnCommand,
            help="External command to spawn when an " "event is received.",
        )

        for plugin in getPlugins(IHandler, comet.plugins):
            proc_group.add_argument(
                f"--{plugin.name}",
                help=f"Enable the {plugin.name} plugin.",
                action="append_const",
                const=plugin.name,
                dest="plugins",
            )
            if IHasOptions.providedBy(plugin):
                for name, default, description in plugin.get_options():
                    proc_group.add_argument(
                        f"--{plugin.name}-{name}", default=default, help=description
                    )

    def _checkOptions(self):
        self._check_for_ivoid()
        self._configure_plugins()

    def _configure_plugins(self):
        """Internal-use method to configure any plugins requested."""
        if self._config.handlers is None:
            self._config.handlers = []
        if self._config.plugins:
            for plugin in getPlugins(IHandler, comet.plugins):
                if plugin.name in self._config.plugins:
                    if IHasOptions.providedBy(plugin):
                        for name, _, _ in plugin.get_options():
                            plugin.set_option(
                                name,
                                getattr(
                                    self._config,
                                    f"{plugin.name}-{name}".replace("-", "_"),
                                ),
                            )
                    self._config.handlers.append(plugin)

    def _check_for_ivoid(self):
        """Ensure that an IVOID has been supplied if broadcasting or receiving."""
        if not self["local_ivo"] and (self["receive"] or self["broadcast"]):
            self.parser.error("IVOA identifier required (--local-ivo).")


def makeService(config):
    event_db = Event_DB(config["eventdb"])
    LoopingCall(event_db.prune, MAX_AGE).start(PRUNE_INTERVAL)

    broker_service = MultiService()
    for ep in config["broadcast"] if config["broadcast"] else []:
        bcast = makeBroadcasterService(
            ep,
            config["local_ivo"],
            config["broadcast_test_interval"],
            config["broadcast_whitelist"],
        )
        bcast.setServiceParent(broker_service)

        # If we're running a broadcast, we will rebroadcast any events we
        # receive to it.
        config["handlers"].append(EventRelay(bcast.factory))

    if config["receive"]:
        validators = [
            CheckPreviouslySeen(event_db),
            CheckSchema(os.path.join(comet.__path__[0], "schema/VOEvent-v2.0.xsd")),
            CheckIVOID(),
        ]
        for ep in config["receive"]:
            recv = makeReceiverService(
                ep,
                config["local_ivo"],
                validators,
                config["handlers"],
                config["receive_whitelist"],
            )
            recv.setServiceParent(broker_service)

    for ep in config["subscribe"] if config["subscribe"] else []:
        sub = makeSubscriberService(
            ep,
            config["local_ivo"],
            [CheckPreviouslySeen(event_db)],
            config["handlers"],
            config["filters"],
        )
        sub.setServiceParent(broker_service)

    if not broker_service.services:
        reactor.callWhenRunning(log.warn, "No services requested; stopping.")
        reactor.callWhenRunning(reactor.stop)
    return broker_service
