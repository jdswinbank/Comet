#!/bin/bash

COMETDIR=$HOME/comet
LOGFILE=$COMETDIR/log/`date +%F-%H-%M`.txt
COMMAND=$COMETDIR/archive_voe_to_file.py
IVORN=some.webaddress.com/nodename 

mkdir -p $COMETDIR/log
mkdir -p $COMETDIR/db

/usr/local/bin/twistd -l $LOGFILE -n comet -r -b --remote=voevent.dc3.com:8099 --remote=someotherserver.com:8099 --cmd=$COMMAND --ivorndb=$COMETDIR/db --local-ivo=ivo://$IVORN


