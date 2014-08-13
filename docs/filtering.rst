.. _sec-filtering:

Filtering
=========

As the number of events on the VOEvent backbone increases, it is unlikely that
individual subscribers will wish to receive or act upon all of them. Comet
therefore implements an experimental filtering system which enables
subscribers to express their preferences as to which events to receive.

At any time, the subscriber may send the broker an authentication response
message. (Note that in the current implementation no authentication is
actually requred, and the processing of digital signatures is not supported).
Within the ``<Meta />`` section of the authentication packet, one or more
XPath expressions may be supplied in ``<Param />`` elements with a ``name``
attribute equal to ``xpath-filter``. For example, the following will select
all VOEvent packets which are not marked as a test::

  <trn:Transport version="1.0" role="authenticate"
    xmlns:trn="http://www.telescope-networks.org/xml/Transport/v1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://telescope-networks.org/schema/Transport/v1.1
      http://www.telescope-networks.org/schema/Transport-v1.1.xsd">
    <Origin>ivo://origin</Origin>
    <Response>ivo://response</Response>
    <TimeStamp>2012-02-08T21:13:53Z</TimeStamp>
    <Meta>
      <Param name"xpath-filter" value="/*[local-name()=&quot;VOEvent&quot; and @role!=&quot;test&quot;]" />
    </Meta>
  </trn:Transport>

The broker will evaluate each filter against each VOEvent packet it processes,
and only forward it to the subscriber if one (or more) of the filters returns
a positive result.

It is worth noting that XPath expressions may return one of four different
types of result: a boolean, a floating point number, a string, or a node-set.
For the purposes of filtering, we regard a positive result as a boolean true,
a non-zero number, a non-empty string, or a non-empty node-set.

When evaluating the XPath expression, no namespaces are defined. In other
words, an expression such as ``//voe::VOEvent`` will not match anything (and
hence the use of ``local-name()`` in the example above).

The filtering capabilities of XPath are quite extensive, and the user is
encouraged to experiment. For example, the names and values of individual
paramters within the VOEvent message can be checked::

  //Param[@name="SC_Lat" and @value>600]

Or messages from particular senders selected::

  //Who[AuthorIVORN="ivo://lofar.transients/"]

