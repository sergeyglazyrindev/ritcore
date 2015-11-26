#!/usr/bin/env bash

CUR_DIR=`pwd`
notifyprojectchanged.sh "touch $CUR_DIR/uwsgi-reload" &
runcompass.sh &
