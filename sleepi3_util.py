import configparser
import sys


PROGRAM_VERSION = '1.0'

DEFAULT_I2C_ADDRESS = '0x6E'
DEFAULT_I2C_BUS = '1'

USAGE = """
Usage: sleepi3ctl COMMAND [OPTION...]

Commands:
    -g, get PARAMETER [<VALUE>]        get sleepi3 parameter
    
    -s, set PARAMETER <VALUE>          set sleepi3 parameter
    
    -h, help                           display help and exit
    
    -v, version                        display version and exit
"""[:-1]

GET_USAGE = """
Get Command Usage:
    sleepi3ctl get PARAMETER

Get Command Parameters:
"""[:-1]

GET_PARAMETERS = {
    'extin': '                         external input state',
    'extin-count': '                   seconds that external input is detected',
    'extin-powerdown': '               external input power down enable flag',
    'extin-trigger': '                 external input trigger flag',
    'extout': '                        external output state',
    'restart': '                       auto restart flag',
    'ri-trigger': '                    ring indicator trigger flag',
    'switch': '                        push switch state',
    'switch-count': '                  seconds that push switch is pressed',
    'sleep-timeout': '                 seconds of sleep timeout',
    'watchdog-timeout': '              seconds of watchdog timeout',
    'voltage': '[1|2|active|all]       power supply voltage (default:active)',
    'measurement-interval': '          seconds of voltage measurement interval',
    'restore-voltage': '               millivolts to detect power restoration',
    'uvlo': '                          under voltage lock out',
    'wakeup-flag': '                   wakeup status flag',
    'wakeup-status': '                 wakeup status',
}

SET_USAGE = """
Set Command Usage:
    sleepi3ctl set PARAMETER <VALUE>

Set Command Parameters and Values:
"""[:-1]

SET_PARAMETERS = {
    'extin-powerdown': '<0|1>          external input power down enable flag',
    'extin-trigger': '<0|1>            external input trigger flag',
    'extout': '<0|1>                   external output state',
    'restart': '<0|1>                  auto restart flag',
    'ri-trigger': '<0|1>               ring indicator trigger flag',
    'sleep-timeout': '<0..255>         seconds of sleep timeout',
    'watchdog-timeout': '<0..255>      seconds of watchdog timeout',
    'measurement-interval': '<0..255>  seconds of voltage measurement interval',
    'restore-voltage': '<0..24000>     millivolts to detect power restoration',
    'uvlo': '<0|1>                     under voltage lock out',
}


def _print_flag(reg, flags):
    mask = 0x01
    
    for flag in flags:
        if mask & reg:
            print(flag)
        mask <<= 1


def help(command):
    if command == 'get':
        print(GET_USAGE)
        for key, val in sorted(GET_PARAMETERS.items()):
            print("    {} {}".format(key, val))
    elif command == 'set':
        print(SET_USAGE)
        for key, val in sorted(SET_PARAMETERS.items()):
            print("    {} {}".format(key, val))
    else:
        print(USAGE)
        print(GET_USAGE)
        for key, val in sorted(GET_PARAMETERS.items()):
            print("    {} {}".format(key, val))
        print(SET_USAGE)
        for key, val in sorted(SET_PARAMETERS.items()):
            print("    {} {}".format(key, val))


def version():
    print("sleepi3ctl version {}".format(PROGRAM_VERSION))


def parse_environment(path):
    parser = configparser.ConfigParser()
    parser.read_dict({'DEFAULT': {
        'I2C_ADDRESS': DEFAULT_I2C_ADDRESS,
        'I2C_BUS': DEFAULT_I2C_BUS,
    }})
    
    with open(path, 'r') as file:
        string = file.read()
    
    parser.read_string('[env]' + string)
    env = parser['env']
    
    return env


class Value:
    def __init__(self, regs, props):
        self.reg = regs[props['name']]
    
    def write(self, data):
        self.reg.value = int(data)
     
    def read(self):
        return self.reg.value
    
    def print(self):
        print(self.read())


class Flag:
    def __init__(self, regs, props):
        self.reg = regs[props['name']]
        self.flag = props['flag']
    
    def write(self, data):
        self.reg.flags[self.flag] = int(data)
    
    def read(self):
        return self.reg.flags[self.flag]
    
    def print(self):
        print(self.read())


class Voltage:
    def __init__(self, regs, props):
        self.regs = regs
        self.channel = props['value']
    
    def read(self):
        if self.channel == '1':
            return "{}".format(self.regs['voltage1'].read())
        elif self.channel == '2':
            return "{}".format(self.regs['voltage2'].read())
        elif self.channel == 'all':
            return "{} {}".format(self.regs['voltage1'].read(),
                                  self.regs['voltage2'].read())
        else:
            v1 = self.regs['voltage1'].read()
            v2 = self.regs['voltage2'].read()
            return v1 if v1 > v2 else v2
    
    def print(self):
        print(self.read())
    

class WakeupFlags(Value):
    def print(self):
        flags = (
            'poweron',
            'watchdog',
            'alarm',
            'switch',
            'extin',
            'ri',
            'restoration',
        )
        _print_flag(self.read(), flags)
    

class Sleepi3Cli:
    
    def __init__(self, sleepi3):
        self.sleepi3 = sleepi3
        self.table = {
            'extin': {
                'class': Flag,
                'properties': {
                    'name': 'io_status',
                    'flag': 'ei'
                }
            },
            'extin-count': {
                'class': Value,
                'properties': {
                    'name': 'external_input_count'
                }
            },
            'extin-powerdown': {
                'class': Flag,
                'properties': {
                    'name': 'input_control',
                    'flag': 'eipde'
                }
            },
            'extin-trigger': {
                'class': Flag,
                'properties': {
                    'name': 'input_control',
                    'flag': 'eitrg'
                }
            },
            'extout': {
                'class': Flag,
                'properties': {
                    'name': 'io_status',
                    'flag': 'eo'
                }
            },
            'restart': { 
                'class': Flag,
                'properties': {
                    'name': 'watchdog_control',
                    'flag': 'rste'
                }
            },
            'ri-trigger': {
                'class': Flag,
                'properties': {
                    'name': 'input_control',
                    'flag': 'ritrg'
                }
            },
            'switch': {
                'class': Flag,
                'properties': {
                    'name': 'io_status',
                    'flag': 'sw'
                }
            },
            'switch-count': {
                'class': Value,
                'properties': {
                    'name': 'push_switch_count'
                }
            },
            'sleep-timeout': {
                'class': Value,
                'properties': {
                    'name': 'sleep_timeout'
                }
            },
            'watchdog-timeout': {
                'class': Value,
                'properties': {
                    'name': 'watchdog_timeout'
                }
            },
            'voltage': {
                'class': Voltage,
                'properties': {
                    'value': ''
                }
            },
            'restore-voltage': {
                'class': Value,
                'properties': {
                    'name': 'restore_voltage'
                }
            },
            'measurement-interval': {
                'class': Value,
                'properties': {
                    'name': 'adc_interval'
                }
            },
            'uvlo': { 
                'class': Flag,
                'properties': {
                    'name': 'watchdog_control',
                    'flag': 'uvlo'
                }
            },
            'wakeup-status': {
                'class': Value,
                'properties': {
                    'name': 'wakeup_status'
                }
            },
            'wakeup-flag': {
                'class': WakeupFlags,
                'properties': {
                    'name': 'wakeup_status'
                }
            }
        }
        
    def version(self):
        version()
    
    def set(self, params):
        if len(params) < 2:
            help('set')
            sys.exit(2)
        name = params[0]
        val = params[1]
        if name not in SET_PARAMETERS.keys():
            help('set')
            sys.exit(2)
        obj = self.table[name]['class'](self.sleepi3.registers, self.table[name]['properties'])
        obj.write(val)
    
    def get(self, params):
        if len(params) < 1:
            help('get')
            sys.exit(2)
        name = params[0]
        if len(params) > 1:
            self.table[name]['properties']['value'] = params[1]
        if name not in GET_PARAMETERS.keys():
            help('get')
            sys.exit(2)
        obj = self.table[name]['class'](self.sleepi3.registers, self.table[name]['properties'])
        obj.print()
    
    def help(self):
        help('all')


