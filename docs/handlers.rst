Event Handlers
==============

Comet aims to server as a fairly complete and fully-functional broker.
However, it is anticipated that those interested in subscribing to VOEvent
feeds may have many and varied requirements: it is impossible to take account
of all of them. For these users, Comet serves as a template and development
platform, and they are encouraged to develop it further to meet their needs.

One way in which the Comet's capabilties may be developed is by providing
"event handlers": Python code which is executed when a new event is received.
In order to make use of this facility, the developer should be familiar with
Twisted's `component architecture
<http://twistedmatrix.com/documents/current/core/howto/components.html>`_.
Handlers may then be written to follow Comet's :class:`comet.icomet.IHandler`
interface, and then installed into the ``comet/plugins directory``. A simple
example is provided in :class:`comet.plugins.eventprinter`. Note that the
plugin class defines a ``__call__()`` method which is invoked with the event
being received as its argument. To be more specific, ``__call__()`` is handed
an instance of :class:`comet.utility.xml.xml_document`.

Each handler must provide a name attribute (e.g. ``print-event``). The user
may specify that a particular plugin be loaded by specifying its name as a
command line argument when invoking comet (``--print-event``).

In some cases, a plugin requires additional configuration. This can be
provided through the use of command line arguments. In this case, the plugin
must also implement the :class:`comet.icomet.IHasOptions` interface. This
involves two further methods: ``get_options()``, which returns a list of
options which are accepted, and ``set_option()``, which provides a means
for setting those options. Options declared in plugins will automatically be
added to the command line options of the :doc:`Comet broker <usage/broker>`.

Again, an example of how such a plugin with options may be implemented is
likely the best documentation: fortunately, one is available in the form of
:class:`comet.plugins.eventwriter`.
