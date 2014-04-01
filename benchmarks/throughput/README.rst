=========================
Comet Throughput Measures
=========================

10000 events are generated on the author side and submitted to a broker with
one connected subscriber. We can measure:

* How long it takes the author to send all the events;
* How long it takes for the broker to receive all the events;
* How long it takes for the subscriber to receive all the events.

The first is in the logging output from ``benchmark.py``. For the other two,
we can read the event dbs.

We can vary the number of simultaneous connections the author opens.

We create a tmpfs on ``/tmp/eventdb`` which we'll use to record the event
databases and log files.

The broker is started::

  $ docker run -d --expose=8098 --expose=8099 --name=comet-broker -v /tmp/eventdb/broker/:/tmp:rw comet:1.1.0-bench twistd -n -repoll comet -r -b

The subscriber is started::

  $ docker docker run -d --link=comet-broker:broker -v /tmp/eventdb/subscriber:/tmp:rw comet:1.1.0-bench bash -c 'twistd -n -repoll comet --remote=${BROKER_PORT_8099_TCP_ADDR}'

We repeat each benchmark 100 times to check that the results are stable. To
run the benchmark, we use a script like this::

  for i in {1..100}
  do
    echo "Run ${i}"
    mkdir -p ./throughput_tests/run${i}
    docker run --link=comet-broker:broker comet:1.1.0-bench bash -c 'benchmark.py -q --host=$BROKER_PORT_8098_TCP_ADDR throughput' > /tmp/eventdb/author.log
    mv /tmp/eventdb/author.log ./throughput_tests/run${i}/author.logi
    mv /tmp/eventdb/broker/comet.broker_test ./throughput_tests/run${i}/broker.db
    mv /tmp/eventdb/subscriber/comet.broker_test ./throughput_tests/run${i}/subscriber.db
  done
