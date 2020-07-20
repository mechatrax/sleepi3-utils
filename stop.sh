#!/bin/sh

if [ "$RETRY_BOOT" != "0" ]
then
	sleepi3ctl set restart 1
else
	sleepi3ctl set restart 0
fi

sleepi3ctl set sleep-timeout $POWEROFF_DELAY
sleepi3ctl set watchdog-timeout $BOOT_TIMEOUT

echo heartbeat > ${LED_PATH}/trigger
