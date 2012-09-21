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
interloper. It is vital to understand *the recipient must always accept
ultimate responsibility as to whether they trust that a particular event is
genuine*: the cryptographic authentication system aims to provide as robust a
guide as possible, decision making remains the job of the end user.

Within the PGP system, a key can be conveniently (but not globally uniquely)
identified by its "key ID", a string of eight hexadecimal digits.  The
*secret* key is protected by a passphrase, which must be supplied whenever the
key is used for signing a message.

Comet's Interaction with ``gpg``
--------------------------------

Comet provides no tools for managing the configuration of ``gpg``. In
particular, the user is responsibly for generating their own key, collecting
keys from others, and managing their trust database using the standard ``gpg``
tools: refer to its documentation for details. Comet will use the ``gpg``
configuration and key database as configured in the user's environment when it
starts: in other words, it will default to ``~/.gpg``, but this can be changed
by exporting the environment variable ``GNUPGHOME`` prior to starting Comet.

Whenever Comet needs the user to specify a key, it expects that key to be
specified according to its hexadecimal key ID.

When a passphrase is needed to unlock a secret key, it cannot be supplied on
the command line for security reasons. Instead, cannot be given on the command
line: instead, it must be written to a file on disk and the filename provided
to Comet. The file should only contain the key passphrase; including any other
characters is an error. Although Comet will not enforce any particular
constraints on the file permissions, it is stronly suggested that the file
should only be accessible to the user running Comet. Comet does not use the
``gpg-agent`` tool to store or retrieve passphrases.

The ``gpg`` system allows for multiple trust levels for signing keys (from
untrusted, through marginally trustworthy, to fully or event ultimately
trusted). In general, however, Comet needs to make a binary "yes or no"
decision for each particular event. It therefore imposes the requirement that
signatures will only be accepted as valid if they are at a minimum regarded as
fully trusted.

Event Authentication
--------------------

Signing an event certifies to the recipient that the holder of a particular
secret key guarantees that the event is trustworthy. In general, the signer is
expected to also be the originator of the event, but, in some circumstances,
it may be an approved notary. In the former case, the user ID associated
with the signing key is expected to be the same as the ``AuthorIVORN`` in the
VOEvent packet. In the latter, the signing key is expected to be countersigned
by a key with a user ID equal to the ``AuthorIVORN`` of the VOEvent packet.

Comet's :ref:`event publisher <sec-sendvo>` makes it possible to sign outgoing
VOEvents by specifying the ``--sign`` option with an appropriate argument.
Note that ``comet-sendvo`` does not enforce any restrictions on the key used,
so long as it is capable of signing: it is up to the user to specify a key
which meets the requirements on the user ID above.

Comet's :ref:`broker <sec-broker>` when running in ``--receive`` mode and if
invoked with the ``--sender-auth`` flag will only accept events which are
signed by a trusted key which meets the user ID requirements specified above.

When running the broker as a *subscriber* (that is, with the ``--remote``
option), the ``--event-auth`` option can be used to specify that received
events should only be acted upon (forwarded to other subscribers, passed to
:ref:`local handlers <sec-handlers>`, or sent to external commands) if they
are properly signed (including the requirements on the ``AuthorIVORN`` outline
above).

Subscriber Authentication
-------------------------

Subscriber authentication makes it possible to limit subscriber connectionions
to the broker to only authorized users (or, rather, only to those users who
hold a valid key). This is achieved by requesting that the subscriber sign an
XML document and return it to the broker; if the broker is not satisfied that
the signer is a valid subscriber, the subscription request is not accepted.
The Comet broker can handle both ends of this transaction: both signing
subscription requests and authenticating its own subscribers based on
signatures.

When invoking Comet as a *subscriber* (that is, with the ``--remote`` option),
the ``--sign`` option can be used to specify that subscription events should
be signed. ``--sign`` requires that the key id and the name of a file
containing the passphrase are supplied as an argument, separated by a colon
(``--sign 12345678:passphrase_file``). Note that only one key and passphrase
can be specified, regardless of how many remote brokers are being connected
to: the same key will be used for all of them.

When invoking Comet as a *broadcaster* (that is, with the ``--broadcast``
option), the ``--subscriber-auth`` option enables authentication of
subscribers. Subscription requests are accepted if the subscriber is able to
present a good, trusted signature made by any key on Comet's keyring: no check
of the key user ID is performed.

.. _Denny: http://www.ivoa.net/Documents/Notes/VOEvent/VOEventDigiSig-20080514.html
.. _OpenPGP: http://www.openpgp.org/
.. _RFC 4880: https://tools.ietf.org/html/rfc4880
.. _GNU Privacy Guard: http://www.gnupg.org/
.. _good references: https://en.wikipedia.org/wiki/Pretty_Good_Privacy
