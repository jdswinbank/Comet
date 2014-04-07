# Comet VOEvent Broker.
# Quick & simple GPG test.
# Relies on the Comet test suite.

import time
import tempfile
import os
import gpgme
import gpgme.editutil
import comet
from comet.utility.voevent import broker_test_message

N_EVENTS = 1000

gpghome = tempfile.mkdtemp(prefix="tmp.gpghome")
os.environ["GNUPGHOME"] = gpghome
ctx = gpgme.Context()

seckey = os.path.join(os.path.dirname(comet.__file__), "test/comet.secret.asc")
pubkey = os.path.join(os.path.dirname(comet.__file__), "test/comet.secret.asc")

with open(seckey, 'r') as k_fp:
    ctx.import_(k_fp)
with open(pubkey, 'r') as k_fp:
    ctx.import_(k_fp)

gpgme.editutil.edit_trust(ctx, ctx.get_key("7C4CA1BD", True), gpgme.VALIDITY_ULTIMATE)

events = []
for _ in range(N_EVENTS):
    ev = broker_test_message("ivo://test")
    ev.sign("comet", "7C4CA1BD")
    events.append(ev)

start = time.time()
for ev in events:
    assert ev.valid_signature()
duration = time.time() - start

print "Number of signatures checked: ", N_EVENTS
print "Total time: ", duration, " s"
print "Time per event: ", duraion / N_EVENTS, " s"
