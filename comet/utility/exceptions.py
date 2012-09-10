class CometException(Exception):
    """
    Base class for Comet exceptions.
    """
    pass

class CometGPGException(CometException):
    """
    Base class for exceptions relating to GPG.
    """
    pass

class CometGPGSigFailedException(CometGPGException):
    """
    Exception thrown when we fail to sign a document.
    """
    pass
