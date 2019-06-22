# Comet VOEvent Broker.
# Base class for command line options.

import os
from argparse import ArgumentParser, ArgumentTypeError

from lxml.etree import XPath, XPathSyntaxError

import comet.plugins
import comet.log as log
from comet.utility.voevent import parse_ivoid, BadIvoidError

__all__ = ["BaseOptions", "valid_ivoid", "valid_xpath"]

class BaseOptions(object):
    def __init__(self):
        if hasattr(self, "PROG"):
            self.parser = ArgumentParser(prog=self.PROG)
        else:
            self.parser = ArgumentParser()
        if "COMET_PLUGINPATH" in os.environ:
            comet.plugins.__path__.extend(
                os.environ.get("COMET_PLUGINPATH").split(":"))

        self.parser.add_argument("--verbose", "-v", action="count",
                                 help="Increase verbosity (may be specified "
                                      "more than once).")
        self._configureParser()

    def parseOptions(self, argv=None):
        """Parse argument list and set option values.

        Parameters
        ----------
        argv : iterable of `str`, optional
            Set of arguments to parse. If unspecified, we rely on argparse to
            pull appropriate values from `sys.argv`.

        Returns
        -------
        self : `Options`
            This object, as a convenience -- try ``Options().parse_options()``.

        Notes
        -----
        This delegates to self.parser.parse_args for the bulk of the work, but
        can also be used to add clean-up actions, etc.
        """
        self._config = self.parser.parse_args(argv)
        if self['verbose'] and self['verbose'] >= 2:
            log.LEVEL = log.Levels.DEBUG
        elif self['verbose'] and self['verbose'] >= 1:
            log.LEVEL = log.Levels.INFO
        else:
            log.LEVEL = log.Levels.WARNING
        self._checkOptions()
        return self

    def _configureParser(self):
        """Add any required options to the parser.

        Override in subclasses.
        """
        pass

    def _checkOptions(self):
        """Perform any sanity checking required on the parsed options.

        Override in subclasses.
        """
        pass

    def __getitem__(self, key):
        """Delegate item lookup to the associated `argparse.Namespace`.
        """
        if hasattr(self, "_config") and hasattr(self._config, key):
            return getattr(self._config, key)
        raise KeyError(key)

    def __contains__(self, key):
        if hasattr(self, "_config"):
            return hasattr(self._config, key)
        else:
            return False

def valid_ivoid(expression):
    """Check for a valid IVOID.

    Parameters
    ----------
    expression : `str`
        Expression to check.

    Returns
    -------
    expression : `str`
        Identical to input.

    Raises
    ------
    ArgumentTypeError
        If `expression` is not a valid IVOID.
    """
    try:
        parse_ivoid(expression)
    except BadIvoidError as e:
        raise ArgumentTypeError(f"Invalid IVOA identifier: {expression}; "
                                f"Required format: "
                                f"ivo://authorityID/resourceKey#local_ID") from e
    return expression

def valid_xpath(expression):
    """Check for a valid XPath filter.

    Parameters
    ----------
    expression : `str`
        Expression to check.

    Returns
    -------
    expression : `str`
        Identical to input.

    Raises
    ------
    ArgumentTypeError
        If `expression` is not a valid XPath expression.
    """
    try:
        XPath(expression)
    except XPathSyntaxError as e:
        raise ArgumentTypeError(f"Invalid XPath expression: "
                                f"{expression}") from e
    return expression
