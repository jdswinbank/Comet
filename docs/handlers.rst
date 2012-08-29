.. _sec-handlers:

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
example is provided in :class:`comet.plugins.eventprinter`.

Each handler must provide a name attribute. The user may specify the names of
one or more handlers to use on the command line (the ``--action`` command line
argument).
