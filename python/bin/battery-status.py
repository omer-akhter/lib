#!/usr/bin/env python2

import logging
import os


def battery_status_linux_2_6_24():
    path_base = '/sys/class/power_supply/'
    len_dash = 20

    str_indent = ' ' * 2
    str_dash = '-' * len_dash
    
    for x in os.listdir(path_base):
        if not x.startswith('BAT'):
            continue

        battery_dir = os.path.join(path_base, x)
        logging.debug('battery info directory: %s', battery_dir)
        battery_dir = os.path.realpath(battery_dir)
        logging.debug('battery info directory: %s', battery_dir)
        battery_dir = os.path.abspath(battery_dir)
        logging.debug('battery info directory: %s', battery_dir)
        battery_dir = os.path.normpath(battery_dir)
        logging.debug('battery info directory: %s', battery_dir)

        print str_dash
        print 'battery %s:' % x[3:]
        print str_dash

        charge_now = charge_max = charge_factory = status = None

        with open(os.path.join(battery_dir, 'charge_now')) as f:
            charge_now = int(f.read().strip())

        with open(os.path.join(battery_dir, 'charge_full')) as f:
            charge_max = int(f.read().strip())

        with open(os.path.join(battery_dir, 'charge_full_design')) as f:
            charge_factory = int(f.read().strip())

        with open(os.path.join(battery_dir, 'status')) as f:
            status = f.read().strip().lower()

        if charge_max is not None:
            if charge_now is not None:
                print str_indent + 'charge:   % .02f' % (charge_now * 100.0 / charge_max)
            if charge_factory is not None:
                print str_indent + 'capacity: %0.02f' % (charge_max * 100.0 / charge_factory)
        
        if status is not None:
                print str_indent + 'status:   %s' % status
        print str_dash


def main():
    import platform
    import re
    path_base = None
    if platform.system().lower() == 'linux':
        release = platform.release().lower()
        version = re.split('[^\d\.]', release, 1)[0]
        logging.info('linux %s', version)
        version = map(int, version.split('.'))

        assert len(version) == 3

        # >= 2.6.24
        if version[0] > 2:
            battery_status_linux_2_6_24()
        elif version[0] == 2 and version[1] > 7:
            battery_status_linux_2_6_24()
        elif version[0] == 2 and version[1] == 6 and version[2] >= 24:
            battery_status_linux_2_6_24()
        else:
            logging.error('linux kernel too old')
    else:
        logging.error('unknown platform')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelno)s: %(message)s',
        level=logging.DEBUG)
    main()
