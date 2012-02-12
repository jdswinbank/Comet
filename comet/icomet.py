# Comet VOEvent Broker
# Interfaces.
# John Swinbank, <swinbank@transientkp.org>, 2012.

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

class IValidator(Interface):
    """
    Called to validate VOEvents before handling.
    """
    def __call__(event):
        """
        Process the event.
        """
