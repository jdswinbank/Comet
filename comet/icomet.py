# Comet VOEvent Broker.
# Standard interfaces definitions.

from zope.interface import Interface, Attribute

class IHandler(Interface):
    """
    Called to process VOEvents which have been received.
    """
    def __call__(event):
        """
        Process the event.
        """

    name = Attribute("Name of this handler.")


class IHasOptions(Interface):
    def get_options():
        """
        Return an iterable of (name, default, description) iterators which may
        be used as command line options.
        """

    def set_option(name, value):
        """
        Set the option named name to the value value.
        """

class IValidator(Interface):
    """
    Called to validate VOEvents before handling.
    """
    def __call__(event):
        """
        Process the event.

        If the event validates, we return normally. If the event is invalid,
        raise an exception.
        """
