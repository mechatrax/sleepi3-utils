#!/bin/sh

timeout=$1
pid=$2
  
for i in `seq $timeout`
do
  sleep 1
  ps -p $pid || exit 0
done

kill -s TERM $pid

sleep 1

ps -p $pid || exit 1

kill -s KILL $pid

exit 2

