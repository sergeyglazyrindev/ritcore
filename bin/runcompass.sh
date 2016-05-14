#!/usr/bin/env bash

cmd_dir=`pwd`
pidfile="$cmd_dir/.sass.pid"
logfile="$cmd_dir/.sass.log"
if [ -f $pidfile ]; then
    kill -9 `cat $pidfile` >/dev/null 2>&1
    [ "$1" = "stop" ] && echo 'shutdown!' && exit 0;
fi
nohup compass watch static>$logfile 2>&1&
echo $! >$pidfile
echo "compass watch success, pid: $!";
