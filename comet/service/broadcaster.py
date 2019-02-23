# Comet VOEvent Broker.

from twisted.application.internet import StreamServerEndpointService
from twisted.internet.endpoints import serverFromString

import comet.log as log
from comet.utility import WhitelistingFactory
from comet.protocol import VOEventBroadcasterFactory

__all__ = ["makeBroadcasterService"]

def makeBroadcasterService(reactor, endpoint, local_ivo, test_interval,
                           whitelist):
    """Create a VOEvent receiver service.

    The receiver service accepts VOEvent messages submitted to the broker by
    authors.

    Parameters
    ----------
    reactor : implements `IReactorCore`
        The reactor which will host the serice.
    endpoint : `str`
        The endpoint to which the service will connect.
    local_ivo : `str`
        IVOA identifier for the subscriber.
    test_interval: `int`
        The interval in seconds between test events to be broadcast. If ``0``,
        no test events will be sent.
    whitelist : `list` of `ipaddress.IPv4Network` or `ipaddress.IPv6Network`
        Only addresses which fall in a network included in the whitelist are
        permitted to subscribe.

    Warnings
    --------
    Although a non-TCP endpoint can be specified (a Unix domain socket, for
    example), the whitelist won't be applied to it correctly (indeed, it will
    probably break horribly).
    """
    server_endpoint = serverFromString(reactor, endpoint)
    factory = VOEventBroadcasterFactory(local_ivo, test_interval)
    if log.LEVEL >= log.Levels.INFO:
        factory.noisy = False

    whitelisting_factory = WhitelistingFactory(factory, whitelist,
                                               "subscription")
    if log.LEVEL >= log.Levels.INFO:
        whitelisting_factory.noisy = False

    service = StreamServerEndpointService(server_endpoint, whitelisting_factory)
    service.setName("Broadcaster")

    return service
