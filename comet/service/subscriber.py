# Comet VOEvent Broker.

from twisted.application.internet import ClientService

from comet.protocol.subscriber import VOEventSubscriberFactory

__all__ = ["makeSubscriberService"]


def makeSubscriberService(endpoint, local_ivo, validators, handlers, filters):
    """Create a reconnecting VOEvent subscriber service.

    Parameters
    ----------
    endpoint : implements `twisted.internet.interfaces.IStreamClientEndpoint`
        The endpoint to which the service will connect.
    local_ivo : `str` or `None`
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
    factory = VOEventSubscriberFactory(local_ivo, validators, handlers, filters)
    service = ClientService(endpoint, factory)

    return service
