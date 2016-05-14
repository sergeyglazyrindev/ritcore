#!/usr/bin/env bash

CUR_DIR=`pwd`
runcompass.sh
notifyprojectchanged.sh "touch $CUR_DIR/uwsgi-reload" &
