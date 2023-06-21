#!/usr/bin/env python3

import sys
from importlib import machinery, util
from pathlib import Path

sys.dont_write_bytecode = True

path = Path('/usr/sbin/sleepi3ctl')

loader = machinery.SourceFileLoader(str(path), str(path))
spec = util.spec_from_file_location(str(path), path, loader=loader)
sleepi3ctl = util.module_from_spec(spec)
spec.loader.exec_module(sleepi3ctl)


ENVIRONMENT_FILE = '/etc/default/sleepi3'


def start(env):
    sleepi3ctl.main(['set', 'extin-trigger', '0'])
    sleepi3ctl.main(['set', 'ri-trigger', '0'])
    sleepi3ctl.main(['set', 'extin-powerdown', env['EXTIN_FORCED_SHUTDOWN']])
    sleepi3ctl.main(['set', 'watchdog-timeout', env['HEARTBEAT_TIMEOUT']])
    sleepi3ctl.main(['set', 'restart', '1'])
    sleepi3ctl.main(['set', 'measurement-interval', '1'])
    sleepi3ctl.main(['set', 'restore-voltage', '0'])
    sleepi3ctl.main(['set', 'uvlo', '0'])
    

def stop(env):
    if env['RETRY_BOOT'] != 0:
        sleepi3ctl.main(['set', 'restart', '1'])
    else:
        sleepi3ctl.main(['set', 'restart', '0'])
    sleepi3ctl.main(['set', 'sleep-timeout', env['POWEROFF_DELAY']])
    sleepi3ctl.main(['set', 'watchdog-timeout', env['BOOT_TIMEOUT']])
    

def restart(env):
    if env['RETRY_BOOT'] != 0:
        sleepi3ctl.main(['set', 'restart', '1'])
    else:
        sleepi3ctl.main(['set', 'restart', '0'])
    sleepi3ctl.main(['set', 'sleep-timeout', '0'])
    sleepi3ctl.main(['set', 'watchdog-timeout', env['BOOT_TIMEOUT']])
    

if __name__ == '__main__':
    arg = sys.argv[1]
    env = sleepi3ctl.parse_environment(ENVIRONMENT_FILE)
    if arg == 'start':
        start(env)
    elif arg == 'stop':
        stop(env)
    elif arg == 'restart':
        restart(env)

