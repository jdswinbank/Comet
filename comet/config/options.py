from twisted.python import usage

class BaseOptions(usage.Options):
    optParameters = [
        ["local-ivo", None, "ivo://comet.broker/default_ivo"]
    ]
