FROM ubuntu:precise
MAINTAINER John Swinbank <j.swinbank@uva.nl>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -q -y python-twisted python-lxml python-ipaddr python-pip python-numpy

RUN pip install comet==1.1.0
ADD latency.py /usr/local/lib/python2.7/dist-packages/comet/plugins/
ADD vtp-bench.py /usr/local/bin/
ADD eventdb-bench.py /usr/local/bin/
ADD gpg-bench.py /usr/local/bin/
ADD xml-bench.py /usr/local/bin/
RUN chmod a+x /usr/local/bin/vtp-bench.py
RUN chmod a+x /usr/local/bin/eventdb-bench.py
RUN chmod a+x /usr/local/bin/gpg-bench.py
RUN chmod a+x /usr/local/bin/xml-bench.py
