#!/usr/bin/python3

import os
import time

hb_out = os.environ['LED_PATH'] + '/brightness'

with open(hb_out, mode='w', buffering=1) as f:
    f.write('0\n')
    while True:
        for br in ['255\n', '0\n'] * 2:
            f.write(br)
            time.sleep(0.1)
        time.sleep(0.6)
