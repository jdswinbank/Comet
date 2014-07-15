================
Comet Benchmarks
================

Throughput Measures
-------------------

10000 events are generated on the author side and submitted to a broker with
one connected subscriber. We can measure:

* How long it takes the author to send all the events;
* How long it takes for the broker to receive all the events;
* How long it takes for the subscriber to receive all the events.

The first is in the logging output from ``vtp-bench.py``. For the other two,
we can read the event dbs.

We can vary the number of simultaneous connections the author opens.

We create a tmpfs on ``/tmp/eventdb`` which we'll use to record the event
databases and log files.

The broker is started::

  $ docker run -d --expose=8098 --expose=8099 --name=comet-broker -v /tmp/eventdb/broker/:/tmp:rw comet:1.1.0-bench twistd -n -repoll comet -r -b

The subscriber is started::

  $ docker docker run -d --link=comet-broker:broker -v /tmp/eventdb/subscriber:/tmp:rw comet:1.1.0-bench bash -c 'twistd -n -repoll comet --remote=${BROKER_PORT_8099_TCP_ADDR}'

We can repeat each bencmark N times to check if the results are stable. To do
that, we use script like this::

  for i in {1..100}
  do
    mkdir -p ./throughput_tests/run${i}
    echo "Starting broker:"
    broker=$(docker.io run -d --expose=8098 --expose=8099 --name=comet-broker -v /tmp/eventdb/broker/:/tmp:rw comet:1.1.0-bench twistd -n -repoll comet -r -b)
    echo "Starting subscriber:"
    sub=$(docker.io run -d --link=comet-broker:broker -v /tmp/eventdb/subscriber:/tmp:rw comet:1.1.0-bench bash -c 'twistd -n -repoll comet --remote=${BROKER_PORT_8099_TCP_ADDR}')
    sleep 1
    docker run --link=comet-broker:broker comet:1.1.0-bench bash -c 'vtp-bench.py -q --host=$BROKER_PORT_8098_TCP_ADDR throughput' > /tmp/eventdb/author.log
    docker.io stop ${sub}
    docker.io stop ${broker}
    docker.io rm ${sub}
    docker.io rm ${broker}
    mv /tmp/eventdb/author.log ./throughput_tests/run${i}/author.logi
    mv /tmp/eventdb/broker/comet.broker_test ./throughput_tests/run${i}/broker.db
    mv /tmp/eventdb/subscriber/comet.broker_test ./throughput_tests/run${i}/subscriber.db
  done

We can also introduce latency to the network interface::

  sudo tc qdisc add dev vethXXXX root netem delay 100ms

We store the results in a directory tree with structure
``${latency}ms/${n_clients}c/run{N}``. These contain both the log from the
author and the event databases from the broker and the subscriber. We
translate this into a JSON summary of the results using
``throughtput_aggregate.py``.


Multi-Subscriber Latency
------------------------

We set up a Comet broker and provide it with N subscribers. All are using
epoll, and writing the event db to tmpfs.

We use ``vtp-bench.py`` to generate 1000 events and submit them to the broker.
Each subscriber keeps track of the latency of events received, writing the log
files stored in the obvious places here.

Note that at 256 subscribers we started to hit the limits of what pc-swinbank
was capable of in two ways:

* It's hard to start more than ~200 Docker instances, as you run out of open
  files. Modified the init script to call ulimit -n before starting Docker to
  work around this.

* Each twisted process uses about 32 MB of memory. Once we hit 256 processes,
  plus the broker, plus the other services on the machine, we start swapping.

We store the log from the ``latency.py`` plugin in a directory structure
labelled by the number of subscribers and then generate aggregate data into
JSON format using ``multisubscriber_aggregate.py``.


Comet Latency Measures
----------------------

We used ``vtp-bench.py`` to generate 3000 events and submit them to the Comet
broker. The broker had one subscriber, running on the same host but in a
different Docker instance. That subscriber received all the events and used
the ``latency`` plugin to measure the time between event generation and
receipt.

We did this three times: once with a "default" setup, once when both broker
and subscriber were using the EPoll reactor, and once with both the EPoll
reactor and storing the event database on tmpfs (ie, a RAM disk). The
latencies are in the three appropriately named log files.

The pythons script plots histograms showing how the latencies compare.
