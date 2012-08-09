======================================
OpenPGP Signatures, Comet and VOEvents
======================================
--------------------------
John Swinbank, August 2012
--------------------------

Introduction
------------

The basic VOEvent packet structure provides no guarantees as to the integrity
of the data contained: it does not guarantee the identity of the event author
or that the event has not been tampered with in transport. It is the position
of the author that this information is fundamental: as we move to a future of
autonomous, automatic telescopes, it is essential that valuable obsevating
time and resources are not triggered by malicious or mistaken VOEvent
messages.

There is widespread agreement that the solution is cryptographic: some form of
digitial signature is applied to the event by its author, and this can then be
verified by the receiver before the event is acted upon. Unfortunately, the
application of cryptographic signatures to XML documents is non-trivial: the
"standard" solution defined in the W3C recommendation `XML Signature Syntax
and Processing`_ (hereafter "XML-DSig") is long, complex and `widely
criticised`_, and library support for many common programming langauges is
hard to come by. Further, adopting the "enveloped" signature system described
by XML-DSig would require changes to the existing `VOEvent schema`_, while the
alternative "detached" mechanism introduces extra complexity for transport
protocols.

Work has already been done on this topic within the VOEvent community.
`Allen`_ described the application of XML-DSig to VOEvent messages, while
`Denny`_ proposed an alternative approach based on the `OpenPGP`_ system.
Denny describes the infrastructure around the OpenPGP system in some detail,
and the reader is encouraged to familiarize themself with that document for an
overview of the situation.

It is the opinion of the present author that neither of these systems provide
a panacea for the issues surrounding VOEvent authentication. However, the
complexity surrounding XML-DSig makes the barrier-to-entry very high. Until
either the XML-DSig technology matures to overcome the technical criticisms
and lower the development effort required, or the OpenPGP solution is
demonstrated to be inadequate to the requirements of the community, `Comet`_
development will concentrate on adding support for OpenPGP signatures.

Infosets, Serialization and Canonicalization
--------------------------------------------

It is important to distinguish between the information contents of a VOEvent
-- the "infoset" -- and a particular representation of that information. The
same infoset can be described by many different VOEvent serializations, all
equally valid according to the `relevant standards`_. The differences may be
as simple, for instance, as a change in the white space used within the
document.

All of the cryptographic signature systems discussed apply at the fundamental
level to a stream of bytes. Therefore, while changing the serialization of a
particular infoset may be valid within the scope of the VOEvent standard, it
will invalidate a signature which has been calculated over the original
serialization.

The XML-DSig standard attempts to overcome many of these limitations by
invoking a "`canonicalization`_" process which transforms the infoset into a
standard representation which both the signing and validating party can
unambiguously agree upon. Unfortunately, this procedure is complex and can be
slow and fragile.

OpenPGP makes no attempt to canonicalize: it simply provides a signature which
applies to the stream of bytes supplied to it. This means that it is not
possible to use a signature calculated over one serialization of a VOEvent to
validate the contents of another serialization, *even if the information
content is identical*. While this is not relevant for simple transmission from
an author through one or more brokers to a receiver, it does significantly
limit the more general applicability of the signature. For example, it would
not be possible to run a service which receives signed VOEvents, deserializes
the information a store such as a relation database, and then later
reconstitutes them as XML including a valid signature from the original
author.

Design Goals
------------

Given the caveat above, the goals for the system set out by this document
necessarily limited.

* The aim of the system being proposed is to make it possible to append an
  OpenPGP signature to an XML element being transmitted using the TCP-based
  `VOEvent Transport Protocol`_ (VTP).

* The signature enables the receiver of the element to verify the identity of
  the sender, using the standard OpenPGP "web of trust" principle. This document
  does not describe how the systems at either end of the transmission should
  manage their keychains, nor does it mandate what the receiver should regard as
  sufficiently trustworthy: these decisions should be made according to local
  requriements.

* The signature is valid for the particular bytestream being transmistted, and
  is invalidated by any manipulation or reserialization of that bytestream.

* The signature should not interfere with processing of the VOEvent by systems
  which do not understand or (wish to) participate in the authentication
  infrastucture: these should be able to treat the event as if it were unsigned.

* The application or removal of the signature should not in any way alter the
  contents of the XML element being transmitted.

Note that the above goals make this proposal suitable for use not only in
signing VOEvents transmitted by VTP but also for use in the subscriber
authentication scheme defined in the VTP standard.

The Cleartext Signature Framework
---------------------------------

Denny proposes that VOEvents should be signed using the `cleartext signature
framework`_ defined in `RFC 4880`_ (OpenPGP Message Format). However, further
investigation demonstrates the shortcomings of this technique, and it is here
that the present document diverges from Denny's proposal.

RFC 4880 section 7 states

  this [cleartext signature] framework is not intended to be reversible.

In other words, cleartext signatures are transformational: applying one to an
XML document could alter its contents. This renders it unsuitable according to
the `Design Goals`_ outlined above.

It is worth noting that the circumstances under which cleartext signatures are
transformation are quite limited: they concern escape sequences applied to
lines starting with a dash "-" (0x2D). The cleartext signature framework is
therefore likely to work perfectly well for the vast majority of VOEvents, but
the chance of an error is ever-present.

Implementation Details
----------------------

To meet the requirements of the section above, this document proposes signing
relevant XML elements using a `detached signature`_. A detached signature is
non-transformational over the text being signed, and therefore avoids the
problems described above.

The cleartext signature framework makes it clear exactly which bytes it is
being applied over by the use of delimeters such as ``=====BEGIN PGP SIGNED
MESSAGE=====``. These do not apply to a detached signature. Therefore, we
propose that the contents of the signed element consist of all bytes from the
opening ``<`` to the closing ``>`` of the element being signed. For example::

  <?xml version="1.0" encoding="UTF-8"?>
  <!-- This text is not signed -->
  <voe:VOEvent xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" ..>
    <!-- all of this text is signed -->
  </voe:VOEvent>

In this case, all of the text from the first character of the string
``<voe:VOEvent`` to the last character of the string ``</voe:VOEvent>`` is
signed, but no bytes outside those delimeters are included.

The signature is ASCII-armoured and appended to the message text as an XML
comment. XML comments are started by the string ``<!--`` and closed by the
string ``-->``.  With XML comments, the string ``--`` is forbidden. The string
``-----`` is used to delimit ASCII-armoured OpenPGP signature blocks. Within
the context of the signed XML element, therefore, the sender must globally
replace ``-----`` with the string ``=====``.  This substitution must be
reversed by the receiver before the ASCII armoured signature is decoded.  All
other characters `which are permitted in ASCII armoured OpenPGP signatures`_
are also valid within XML comments, so no other substitution is required.

An example of a signed VOEvent with the above substitution performed is::

  <?xml version="1.0" encoding="UTF-8"?>
  <!-- This text is not signed -->
  <voe:VOEvent xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" ..>
    <!-- all of this text is signed -->
  </voe:VOEvent><!--
  =====BEGIN PGP SIGNATURE=====
  Version: GnuPG v1.4.12 (Darwin)

  iQEcBAABAgAGBQJQIpY+AAoJEA7iIKe6Xi++k1AH/jW+7ql3coxbvJV41fhFTHOr
  dPv+4woSXPvZXX2s3D0SEfSvtE2ofuQlzrGojGYgqZ9gwJS8/bjGGehTr29jA50e
  92kYGenaCtti7BhatPVOwLETTsIx5Yj/3sbuIQhL8mWPW9oO6/0VNnbefaqZ7KZp
  oBb8T3y2wkVF0Odz1lLKCVVyGZWdXM77m4PeVQeH8/6yqhrFl4npUPpR7Y4020+U
  XkqZnERprPfiKF4j/OQpn4rtsKFlxwLgVUgalPAav0OjYyDjZrTG7vn4ZFCrInIT
  F5P990K1jvSuA8TD7xUXZmceEM3yHm+/x5f5vCe6pZvRAsFZqAkfm11v0pxr5K4=
  =nZgJ
  =====END PGP SIGNATURE=====

  -->

This system is unambiguously defined only when events are transmitted
according to the VTP system, which specifies that only a single VOEvent or
transport element is transmitted in each transaction. If multiple root-level
XML elements were to be transmitted, it would be ambiguous as to which the
OpenPGP signature referred. This is therefore forbidden by the protocol.

Software
--------

This system relies on the OpenPGP standard as set down in RFC 4880. Various
implementations of the OpenPGP standard are available. All tests carried out
while writing this document have been carried out using the `GNU Privacy
Guard`_, which is freely available and licensed under the `GNU General Public
License`_.

The `Dakota VOEvent Tools`_ provide a working implmentation of the `earlier
proposal by Denny`_.

A version of Comet with basic support for this system is now being tested, and
it will be merged into the released version soon. A preview version is
available to interested parties on request.

Performance
-----------

The performance implications of this system are not negligible. The
cryptographic operations obviously require some computation. Further, `by
design`_, there is no GnuPG shared library: signing or verifying operations
cannot be handled in-process and instead involve forking a separate ``gpg``
executable.

The time taken for signing and verification obviously varies significantly
both with the size of the data being signed and the key used for signing.
Informal tests on a modest, 2009-vintage laptop running `OS X`_ 10.8 and GnuPG
1.4.12 indicate that signing a typical VOEvent message takes on the order of
0.1 seconds, including spawning the ``gpg`` executable, while verifying that
signature takes around 0.01 seconds. On server grade hardware, one would
imagine that this time would be substantially reduced.


.. _XML Signature Syntax and Processing: http://www.w3.org/TR/xmldsig-core/
.. _widely criticised: http://www.cs.auckland.ac.nz/~pgut001/pubs/xmlsec.txt
.. _Allen: http://www3.interscience.wiley.com/cgi-bin/fulltext/117927641/PDFSTART
.. _Denny: http://www.ivoa.net/Documents/latest/VOEventDigiSig.html
.. _OpenPGP: http://www.openpgp.org/
.. _relevant standards: http://www.ivoa.net/Documents/VOEvent/index.html
.. _canonicalization: http://www.w3.org/TR/xml-c14n
.. _VOEvent Transport Protocol: http://www.ivoa.net/Documents/Notes/VOEventTransport/
.. _RFC 4880: https://tools.ietf.org/html/rfc4880
.. _cleartext signature framework: https://tools.ietf.org/html/rfc4880#section-7
.. _detached signature: https://tools.ietf.org/html/rfc4880#section-11.4
.. _which are permitted in ASCII armoured OpenPGP signatures: https://tools.ietf.org/html/rfc4880#section-6.3
.. _GNU Privacy Guard: http://www.gnupg.org/
.. _GNU General Public License: https://www.gnu.org/copyleft/gpl.html
.. _Dakota VOEvent Tools: http://voevent.dc3.com/
.. _earlier proposal by Denny: Denny_
.. _Comet: http://comet.transientskp.org/
.. _by design: http://www.gnupg.org/faq/GnuPG-FAQ.html#cant-we-have-a-gpg-library
.. _OS X: https://www.apple.com/osx/
.. _VOEvent schema: http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd
