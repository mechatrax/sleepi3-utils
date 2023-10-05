#!/usr/bin/env python3

import sys
from importlib import machinery, util
from pathlib import Path

import sleepi


path = Path('/usr/share/sleepi3-utils/sleepi3_util.py')

loader = machinery.SourceFileLoader(str(path), str(path))
spec = util.spec_from_file_location(str(path), path, loader=loader)
sleepi3_util = util.module_from_spec(spec)
spec.loader.exec_module(sleepi3_util)


ENVIRONMENT_FILE = '/etc/default/sleepi3'


def start(cli, env):
    cli.set(['extin-trigger', '0'])
    cli.set(['ri-trigger', '0'])
    cli.set(['extin-powerdown', env['EXTIN_FORCED_SHUTDOWN']])
    cli.set(['watchdog-timeout', env['HEARTBEAT_TIMEOUT']])
    cli.set(['restart', '1'])
    cli.set(['measurement-interval', '1'])
    cli.set(['restore-voltage', '0'])
    cli.set(['uvlo', '0'])
    

def stop(cli, env):
    if env['RETRY_BOOT'] != 0:
        cli.set(['restart', '1'])
    else:
        cli.set(['restart', '0'])
    cli.set(['sleep-timeout', env['POWEROFF_DELAY']])
    cli.set(['watchdog-timeout', env['BOOT_TIMEOUT']])
    

def restart(cli, env):
    if env['RETRY_BOOT'] != 0:
        cli.set(['restart', '1'])
    else:
        cli.set(['restart', '0'])
    cli.set(['sleep-timeout', '0'])
    cli.set(['watchdog-timeout', env['BOOT_TIMEOUT']])
    

if __name__ == '__main__':
    arg = sys.argv[1]
    env = sleepi3_util.parse_environment(ENVIRONMENT_FILE)
    bus = int(env['I2C_BUS'])
    addr = int(env['I2C_ADDRESS'], 16)
    cli = sleepi3_util.Sleepi3Cli(sleepi.Sleepi3(bus, addr))
    
    if arg == 'start':
        start(cli, env)
    elif arg == 'stop':
        stop(cli, env)
    elif arg == 'restart':
        restart(cli, env)

