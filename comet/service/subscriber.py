# Comet VOEvent Broker.

from twisted.application.internet import ClientService
from twisted.internet.endpoints import clientFromString

from comet.protocol.subscriber import VOEventSubscriberFactory

__all__ = ["makeSubscriberService"]

def makeSubscriberService(reactor, endpoint, local_ivo, validators, handlers,
                          filters):
    """Create a reconnecting VOEvent subscriber service.

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
    filters : `list` of `str`
        XPath filters. Will be passed to upstream as a request to filter the
        alerts being sent.

    Notes
    -----
    Upstream brokes may not provide support for XPath filtering; in this case,
    the filters suppplied will be ignored.

    Reconnection is handled according to the default policies of
    `twisted.application.internet.ClientService`.
    """
    client_endpoint = clientFromString(reactor, endpoint)
    subscriber_factory = VOEventSubscriberFactory(
        local_ivo=local_ivo, validators=validators,
        handlers=handlers, filters=filters
    )
    remote_service = ClientService(client_endpoint, subscriber_factory)
    remote_service.setName(f"Remote {endpoint}")
    return remote_service
