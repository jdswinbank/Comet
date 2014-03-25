FROM ubuntu:precise
MAINTAINER John Swinbank <j.swinbank@uva.nl>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -q -y python-twisted python-lxml python-ipaddr python-pip

RUN pip install comet==1.1.0
ADD latency.py /usr/local/lib/python2.7/dist-packages/comet/plugins/
