# Comet VOEvent Broker.
# Utilities for working with Twisted endpoints.

from twisted.internet.endpoints import clientFromString, serverFromString

__all__ = ["coerce_to_client_endpoint", "coerce_to_server_endpoint"]

def coerce_to_client_endpoint(reactor, ep_descr, default_port):
    """Given a string, attempt to produce a client endpoint.

    If the string describes an endpoint directly, we use that; otherwise,
    assume it's an attempt to provide a TCP endpoint and try variations on
    that in the hope that one is parseable.

    Parameters
    ----------
    reactor : `implements twisted.internet.interfaces.IReactorCore`
        Twisted reactor to use in constructing endpoint.
    ep_descr : `str`
        String describing the desired endpoint.
    default_port : `int`
        If `ep_descr` doesn't contain a port, `default_port` is used to
        attempt to build an endpoint.
    """
    try:
        # Maybe this already is a valid endpoint.
        return clientFromString(reactor, ep_descr)
    except (ValueError, TypeError):
        pass
    try:
        # Assume it just needs "tcp:" prepended.
        return clientFromString(reactor, f"tcp:{ep_descr}")
    except (ValueError, TypeError):
        pass
    try:
        # Assume it needs a port number appended.
        return clientFromString(reactor, f"{ep_descr}:{default_port}")
    except (ValueError, TypeError):
        pass
    try:
        # Assume it needs both.
        return clientFromString(reactor, f"tcp:{ep_descr}:{default_port}")
    except (ValueError, TypeError):
        # At this point, we'll give up, and go back to the original bad parse.
        clientFromString(reactor, ep_descr)

def coerce_to_server_endpoint(reactor, ep_descr):
    """Given a string, attempt to produce a server endpoint.

    If the string describes an endpoint directly, we use that; otherwise,
    assume it's an attempt to provide a TCP endpoint and try variations on
    that in the hope that one is parseable.

    Parameters
    ----------
    reactor : `implements twisted.internet.interfaces.IReactorCore`
        Twisted reactor to use in constructing endpoint.
    ep_descr : `str`
        String describing the desired endpoint.
    """
    try:
        # Maybe this already is a valid endpoint.
        return serverFromString(reactor, ep_descr)
    except (ValueError, TypeError):
        pass
    try:
        # Assume it just needs "tcp:" prepended.
        return serverFromString(reactor, f"tcp:{ep_descr}")
    except (ValueError, TypeError):
        # At this point, we'll give up, and go back to the original bad parse.
        serverFromString(reactor, ep_descr)
