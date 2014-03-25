======================
Comet Latency Measures
======================

We used ``benchmark.py`` to generate 3000 events and submit them to the Comet
broker. The broker had one subscriber, running on the same host but in a
different Docker instance. That subscriber received all the events and used
the ``latency`` plugin to measure the time between event generation and
receipt.

We did this three times: once with a "default" setup, once when both broker
and subscriber were using the EPoll reactor, and once with both the EPoll
reactor and storing the event database on tmpfs (ie, a RAM disk). The
latencies are in the three appropriately named log files.

The pythons script plots histograms showing how the latencies compare.
