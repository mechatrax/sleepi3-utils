#!/bin/sh

[ $(sleepi3ctl get wakeup-status) -eq 1 ] && sleepi3alarm clear

sleepi3ctl set extin-trigger 0
sleepi3ctl set ri-trigger 0
sleepi3ctl set extin-powerdown $EXTIN_FORCED_SHUTDOWN
sleepi3ctl set watchdog-timeout $HEARTBEAT_TIMEOUT
sleepi3ctl set restart 1

sleepi3ctl set measurement-interval 1
sleepi3ctl set restore-voltage 0
sleepi3ctl set uvlo 0

