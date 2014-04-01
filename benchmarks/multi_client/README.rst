========================
Multi-Subscriber Latency
========================

We set up a Comet broker and provide it with N subscribers. All are using
epoll, and writing the event db to tmpfs.

We use ``benchmark.py`` to generate 1000 events and submit them to the broker.
Each subscriber keeps track of the latency of events received, writing the log
files stored in the obvious places here.

Note that at 256 subscribers we started to hit the limits of what pc-swinbank
was capable of in two ways:

* It's hard to start more than ~200 Docker instances, as you run out of open
  files. Modified the init script to call ulimit -n before starting Docker to
  work around this.

* Each twisted process uses about 32 MB of memory. Once we hit 256 processes,
  plus the broker, plus the other services on the machine, we start swapping.
