#!/usr/bin/env python2

import logging
import os
import sys
from functools import reduce

path_root, _ = os.path.split(
    os.path.abspath( os.path.dirname( os.path.realpath( __file__ ) ) ) )
sys.path.append( path_root )

import argparse2

SEPARATOR = ':'


def time_seconds( time_str, hours, minutes, seconds, separator=SEPARATOR ):
    time_list = map(
        lambda x: float( x ),
        time_str.strip().split( separator ) )
    if len( time_list ) > 3:
        raise Exception( 'Invalid time specification' )

    time_count = len( time_list )
    time_list += [0.0] * ( 3 - time_count )
    time_list[0] += hours
    time_list[1] += minutes
    time_list[2] += seconds

    interval = reduce( lambda x, y: x * 60.0 + y, time_list )
    return interval


def time_str( seconds, separator=SEPARATOR ):
    time_list = [seconds]
    while len( time_list ) < 3 and time_list[0] > 59:
        t = long( time_list[0] / 60 )
        time_list[0] -= t * 60.0
        time_list.insert( 0, t )

    time_list[-1] = '%02.3f' % time_list[-1]
    time_list[:-1] = map( lambda x: '%02d' % x, time_list[:-1] )
    return separator.join( time_list )


def time_acceled( accel, interval, passed=None ):
    if passed:
        interval -= passed
    return interval / accel


def main():
    default_time = SEPARATOR.join( '0' * 3 )
    parser = argparse2.ArgParser2(
        description='Calculate time interval based on acceleration' )
    parser.add_argument(
        '-x',
        '--separator',
        default=SEPARATOR,
        help='''Separator to use for -t and -u parameters.
Please note that decimal may not be used since it may indicate
a decimal quantity. Defaults to %s''' % SEPARATOR )
    parser.add_argument(
        '-l',
        '--logging',
        type=argparse2.LogType(),
        choices=argparse2.LogType.choices,
        default=logging.DEBUG,
        help='Logging level. Default: info' )

    parser.add_argument(
        '-a',
        '--acceleration',
        type=float,
        default=1.0,
        help='Acceleration. Default: 1.0' )

    parser.add_argument(
        '-H',
        '--hours',
        type=float,
        default=0.0,
        help='Hours. Default: 0.0' )
    parser.add_argument(
        '-M',
        '--minutes',
        type=float,
        default=0.0,
        help='Minutes. Default: 0.0' )
    parser.add_argument(
        '-S',
        '--seconds',
        type=float,
        default=0.0,
        help='Seconds. Default: 0.0' )
    parser.add_argument(
        '-T',
        '--time',
        default=default_time,
        help='Time expressed as string. Can be [H]H[:[M]M[:[S]S]] Default: %s' % default_time )

    parser.add_argument(
        '-p',
        '--passed_hours',
        type=float,
        default=0.0,
        help='Passed Hours. Default: 0.0' )
    parser.add_argument(
        '-q',
        '--passed_minutes',
        type=float,
        default=0.0,
        help='Passed Minutes. Default: 0.0' )
    parser.add_argument(
        '-r',
        '--passed_seconds',
        type=float,
        default=0.0,
        help='Passed Seconds. Default: 0.0' )
    parser.add_argument(
        '-u',
        '--passed_time',
        default=default_time,
        help='Time expressed as string. Can be [H]H[:[M]M[:[S]S]] Default: %s' % default_time )

    args = parser.parse_args()
    if args.logging is None:
        logging.disable( logging.DEBUG )
    else:
        logging.getLogger().setLevel( level=args.logging )

    t1 = time_seconds(
        args.time,
        args.hours,
        args.minutes,
        args.seconds,
        args.separator )
    t2 = time_seconds(
        args.passed_time,
        args.passed_hours,
        args.passed_minutes,
        args.passed_seconds,
        args.separator )

    print time_str( time_acceled( args.acceleration, t1, t2 ), args.separator )

if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelno)s: %(message)s',
        level=logging.DEBUG )
    main()
