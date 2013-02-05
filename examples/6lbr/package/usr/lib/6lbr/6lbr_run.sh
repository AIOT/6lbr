#!/bin/sh

PIDFILE=/var/run/6lbr.pid
LOGS=/var/log
BIN_6LBR=/usr/bin/6lbr
CONF=/etc/6lbr/6lbr.conf

$BIN_6LBR $CONF >> $LOGS/6lbr.log 2>>$LOGS/6lbr.err &
	
echo $! > $PIDFILE
