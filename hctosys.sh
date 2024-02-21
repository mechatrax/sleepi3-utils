#!/bin/sh

DEVICE="/dev/$RTC_DEVICE"
RETRY=2
TIMEOUT=15

[ "$HCTOSYS" = "yes" ] || exit 0

for i in `seq $RETRY`
do
  hwclock -f $DEVICE --hctosys &
  /usr/lib/sleepi3-utils/timeoutpid.sh $TIMEOUT $! && wait $! && exit 0
  sleep 1
done

exit 2
