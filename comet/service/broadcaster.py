# Comet VOEvent Broker.

from twisted.application.internet import StreamServerEndpointService

import comet.log as log
from comet.utility import WhitelistingFactory
from comet.protocol import VOEventBroadcasterFactory

__all__ = ["makeBroadcasterService"]


def makeBroadcasterService(endpoint, local_ivo, test_interval, whitelist):
    """Create a VOEvent receiver service.

    The receiver service accepts VOEvent messages submitted to the broker by
    authors.

    Parameters
    ----------
    endpoint : implements `twisted.internet.interfaces.IStreamServerEndpoint`
        The endpoint to which the service will listen.
    local_ivo : `str`
        IVOA identifier for the subscriber.
    test_interval: `int`
        The interval in seconds between test events to be broadcast. If ``0``,
        no test events will be sent.
    whitelist : `list` of `ipaddress.IPv4Network` or `ipaddress.IPv6Network`
        Only addresses which fall in a network included in the whitelist are
        permitted to subscribe.
    """
    factory = VOEventBroadcasterFactory(local_ivo, test_interval)
    if log.LEVEL >= log.Levels.INFO:
        factory.noisy = False

    whitelisting_factory = WhitelistingFactory(factory, whitelist, "subscription")
    if log.LEVEL >= log.Levels.INFO:
        whitelisting_factory.noisy = False

    service = StreamServerEndpointService(endpoint, whitelisting_factory)

    # Shut down, rather than simply logging an error, if we can't bind.
    service._raiseSynchronously = True

    return service
