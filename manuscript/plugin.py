from zope.interface import implementer
from twisted.plugin import IPlugin
from comet.icomet import IHandler, IHasOptions

# A plugin implements the IPlugin
# and IHandler interfaces
@implementer(IPlugin, IHandler)
class ExamplePlugin(object):
    # The "name" attribute is used to refer
    # to the plugin on the command line.
    name = "example"

    # The "__call__()" method is invoked
    # when a new event is received.
    def __call__(self, event):
        print "Event received"

# The plugin must be instantiated before use.
example_plugin = ExamplePlugin()
