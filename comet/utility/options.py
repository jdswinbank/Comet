# Comet VOEvent Broker.
# Base class for command line options.

from twisted.python import usage
from comet import BINARY_TYPE
from comet.utility.voevent import parse_ivoid

__all__ = ["BaseOptions"]

class BaseOptions(usage.Options):
    optParameters = [
        ["local-ivo", None, None, "IVOA identifier for this system "
                                  "(required for --receive and --broadcast)."]
    ]

    def opt_local_ivo(self, local_ivo):
        # In Python 3, we should receive options as unicode strings. In Python
        # 2, we'll get byte strings. Normalize so they are always unicode.
        if isinstance(local_ivo, BINARY_TYPE):
            local_ivo = local_ivo.decode()
        try:
            parse_ivoid(local_ivo)
        except Exception as e:
            raise usage.UsageError("Invalid IVOA identifier: %s\n  "
                  "Required format: ivo://authorityID/resourceKey#local_ID" % local_ivo)
        self['local-ivo'] = local_ivo

    def postOptions(self):
        if not self['local-ivo'] and (self['broadcast'] or self['receive']):
            raise usage.UsageError("IVOA identifier required (--local-ivo)")
