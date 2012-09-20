.. _sec-authentication:

Authentication
==============

Comet implements a mechanism for authenticating VOEvents and broker
subscribers based on the system proposed by `Denny`_. At time of writing, the
latest published version of that system is 1.1, dated 14 May 2008, which has
some known weaknesses (see the :ref:`relevant appendix <app-crypto>` for
details). An updated version is soon to be released, and it is that which is
adopted here.

The system uses the `OpenPGP`_ standard, as formalized in `RFC 4880`_. In
particular, Comet uses the `GNU Privacy Guard`_ implementation of OpenPGP; it
should, however, interoperate with any compliant implemenation without
difficulty.

It is beyond the scope of this document to describe the workings of PGP in
general: `good references`_ are not hard to find, and Denny's document
provides a convenient overview of its application to VOEvents. Here, suffice
it to say that PGP provides a "public-key" based cryptographic system. A user
generates a pair of keys, one secret and one public. They keep the secret key
confidential, while distributing the public key. The secret key can be used to
sign a message; given the signature, the holder of the public key can verify
that a message is identical (at the byte-for-byte level) to that signed by the
secret key.

An important issue to bear in mind is that the holder of the public key can
only trust that the signature provides a useful guide to the authenticity of
the message if the authenticity of the key pair can be guaranteed: the
recipient must be certain that the secret key corresponding to the public key
they hold really belongs to their intended correspondent rather than an
interloper.

Within the PGP system, a key can be conveniently (but not globally uniquely)
identified by its "key ID", a string of eight hexadecimal digits. It is this
key ID which Comet requires when the user needs to refer to a particular key.

The *secret* key is protected by a passphrase, which must be supplied whenever
the key is used for signing a message. For security reasons, this passphrase
cannot be given on the command line: instead, it must be written to a file on
disk and the filename provided to Comet. The file should only contain the key
passphrase; including any other characters is an error. Although Comet will
not enforce any particular constraints on the file permissions, it is stronly
suggested that the file should only be accessible to the user running Comet.

Event Authentication
--------------------

Subscriber Authentication
-------------------------

.. _Denny: http://www.ivoa.net/Documents/Notes/VOEvent/VOEventDigiSig-20080514.html
.. _OpenPGP: http://www.openpgp.org/
.. _RFC 4880: https://tools.ietf.org/html/rfc4880
.. _GNU Privacy Guard: http://www.gnupg.org/
.. _good references: https://en.wikipedia.org/wiki/Pretty_Good_Privacy
