# Comet VOEvent Broker.

from twisted.application.internet import StreamServerEndpointService
from twisted.internet.endpoints import serverFromString

import comet.log as log
from comet.utility import WhitelistingFactory
from comet.protocol import VOEventReceiverFactory

__all__ = ["makeReceiverService"]

def makeReceiverService(reactor, endpoint, local_ivo, validators, handlers,
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
    validators : `list` of implementers of `~comet.icomet.IValidator`.
        Validators which will be applied to incoming events. Events which fail
        validation will be rejected.
    handlers : `list` of implementers of `~comet.icomet.IHandler`.
        Handlers to which events which pass validation will be passed.
    whitelist : `list` of `ipaddress.IPv4Network` or `ipaddress.IPv6Network`
        Submissions are only accepted from addresses which fall in a network
        included in the whitelist.

    Warnings
    --------
    Although a non-TCP endpoint can be specified (a Unix domain socket, for
    example), the whitelist won't be applied to it correctly (indeed, it will
    probably break horribly).
    """
    server_endpoint = serverFromString(reactor, endpoint)
    receiver_factory = VOEventReceiverFactory(local_ivo=local_ivo,
                                              validators=validators,
                                              handlers=handlers)
    if log.LEVEL >= log.Levels.INFO:
        receiver_factory.noisy = False
    author_whitelisting_factory = WhitelistingFactory(
        receiver_factory, whitelist, "submission"
    )
    if log.LEVEL >= log.Levels.INFO:
        author_whitelisting_factory.noisy = False

    receiver_service = StreamServerEndpointService(server_endpoint,
                                                   author_whitelisting_factory)
    receiver_service.setName("Receiver")

    return receiver_service
