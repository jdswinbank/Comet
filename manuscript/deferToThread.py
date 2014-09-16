from twisted.internet.threads import \
     deferToThread

def deferred_parse(data):
    return deferToThread(parse, data)
