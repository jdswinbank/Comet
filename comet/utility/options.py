from twisted.python import usage
from comet.utility.voevent import parse_ivorn

class BaseOptions(usage.Options):
    optParameters = [
        ["local-ivo", None, None, "IVOA identifier for this system (required)"]
    ]

    def opt_local_ivo(self, local_ivo):
        try:
            parse_ivorn(local_ivo)
        except:
            raise usage.UsageError("Invalid IVOA identifier: %s\n  "
                  "Required format: ivo://authorityID/resourceKey#local_ID" % local_ivo)
        self['local-ivo'] = local_ivo

    def postOptions(self):
        if not self['local-ivo']:
            raise usage.UsageError("IVOA identifier required (--local-ivo)")
