#!/usr/bin/env python2

from collections import defaultdict
from functools import reduce
import csv
import fnmatch
import logging
import os
import re
import subprocess
import sys

import magic


IGNORE_DIRS = ( 
    '.DocumentRevisions-V100',
    '.fseventsd',
    '.Spotlight-V100',
    '.TemporaryItems',
    '.Trashes',
    '.git',
    '.svn' )
IGNORE_FILES = ( '.DS_Store', '.gitignore', '.npmignore' )
RE_IGNORE = map( 
    lambda x: '(?:%s)' %
    fnmatch.translate( x ),
    IGNORE_DIRS +
    IGNORE_FILES )
RE_IGNORE = re.compile( '|'.join( RE_IGNORE ) )

conpath = lambda path_: os.path.abspath( 
    os.path.normpath( 
        os.path.realpath( path_ ) ) )
path_root, _ = os.path.split( os.path.dirname( conpath( __file__ ) ) )
# logging.debug('path_root: %s', path_root)
sys.path.append( path_root )
import argparse2
import ioutil


def bytes_in_unit_str( bytes, decimals=2 ):
    # b = byte, k = kilobytes, ...
    units = 'bkmgt'
    unit = 0

    v = float( bytes )
    while v > 1024:
        v /= 1024.0
        unit += 1

    return ( '%0.' + str( decimals ) + 'f%s' ) % ( v, units[unit] )


def unit_str_in_bytes( val ):
    if isinstance( val, ( int, long ) ):
        return val
    elif isinstance( val, ( str, unicode ) ):
        m = 1
        val = val.strip().lower()
        val_ = val.split( '.' )
        if not val_[-1].isdigit():
            if not val_[-1][:-1].isdigit():
                return None
            try:
                k = 'bkmgt'.index( val_[-1][-1] )
            except:
                return None
            m = 1024 ** k
            val = val[:-1]
        return long( float( val ) * m )
    return None


def collapse_subpath( path_list ):
    path_list = map( lambda x: x.split( os.sep ), path_list )
    paths_zipped = zip( *path_list )

    sub_path = []
    sub_path_len = len( min( path_list, key=lambda x: len( x ) ) )
    for i in xrange( 0, sub_path_len ):
        p = reduce( lambda x, y: x if x == y else None, paths_zipped[i] )
        if p is None:
            break
        else:
            sub_path.append( p )

    sub_path_len = len( sub_path )
    for i in xrange( 0, len( path_list ) ):
        path_list[i] = os.sep.join( path_list[i][sub_path_len:] )

    return ( os.sep.join( sub_path ) + os.sep ), sorted( path_list )


def parse_report( report_str ):
    dup_list = []
    for rep_line in report_str.splitlines():
        rep_line = rep_line.strip()

        if not rep_line:
            continue

        if rep_line.endswith( 'each:' ):
            dup_list_len = len( dup_list )
            if dup_list_len:
                if dup_list[-1][0] == 0:
                    del dup_list[-1]
                else:
                    ignore_list = filter( 
                        None,
                        map( RE_IGNORE.search,
                            dup_list[-1][-1] ) )
                    if ignore_list:
                        logging.debug( 
                            'Ignoring:\n\t%s',
                            '\n\t'.join( dup_list[-1][-1] ) )
                        del dup_list[-1]

            file_size = long( rep_line.split( ' ' )[0] )
            dup_list.append( [file_size, []] )
        else:
            dup_list[-1][-1].append( rep_line )

    dup_list.sort()
    for i, ( dup_bytes, dup_paths ) in enumerate( dup_list ):
        common_prefix, files = collapse_subpath( dup_paths )
        dup_list[i] = {
            'bytes': dup_bytes,
            'size': bytes_in_unit_str( dup_bytes ),
            'paths': dup_paths,
            'common_prefix': common_prefix,
            'files': files,
        }

    return dup_list


def print_list( dup_list, reverse=False ):
    if reverse:
        dup_list = reversed( dup_list )

    total_bytes = 0
    for dup_info in dup_list:
        total_bytes += dup_info['bytes']
        # size with units
        print dup_info['size']
        # common sub-path
        print '\t%s' % dup_info['common_prefix']
        # files
        print '\t\t%s\n' % '\n\t\t'.join( dup_info['files'] )

    print '%d entries, size: %s' % ( len( dup_list ), bytes_in_unit_str( total_bytes ) )


def main_():
    cmd = ['fdupes', '--recurse', '--size'] + sys.argv[1:]
    logging.debug( 'CMD: %s', ' '.join( cmd ) )
    dup_report = subprocess.check_output( cmd )

    dup_list = parse_report( dup_report )
    print_list( dup_list )


def main():
    parser = argparse2.ArgParser2( 
        description='Find duplicate file sets in given paths' )
    parser.add_argument( 
        'path',
        nargs='+',
        type=argparse2.PathType( check_exists=True, is_directory=True ),
        help='path to search within' )

    parser.add_argument( 
        '-o', '--out',
        default='./dups.csv',
        type=argparse2.PathType( check_write=True, is_directory=False ),
        help='file to save output in' )

    parser.add_argument( 
        '-l',
        '--logging',
        type=argparse2.LogType(),
        default=logging.INFO,
        help='Logging level. Default: info' )

    parser.add_argument( 
        '--sizemin',
        default=1,
        help='Minimum file size in bytes; or suffixed with k, m, or g' )

    parser.add_argument( 
        '--sizemax',
        default=0,
        help='Maximum file size in bytes; or suffixed with k, m, or g' )

    parser.add_argument( 
        '--hashblocks',
        default=5,
        type=int,
        help='Maximum blocks (4096 byte chunks) to use for hash calculation. 0 to use entire file. Default is 5.' )

    args = parser.parse_args()
    # if args.logging is None:
    #    logging.disable(logging.DEBUG)
    # else:
    #    logging.getLogger().setLevel(level=args.logging)
    logging.debug( 'args: %s', args )

    sizemin = unit_str_in_bytes( args.sizemin )
    sizemax = unit_str_in_bytes( args.sizemax )
    path_list = validate_paths( args.path )
    logging.info( 'Pass 1/2' )
    dup_list = size_walk( path_list, sizemin, sizemax )
    dup_count = len( dup_list )
    logging.info( 'Found %d duplicate file sets by size\n', dup_count )
    #raw_input()

    '''
    logging.info('Pass 2/3')
    dup_list_ = []
    for i, d_list in enumerate(dup_list):
        logging.debug('Processing %s/%s', i + 1, dup_count)
        dup_list_.extend(mime_walk(d_list))

    dup_list = dup_list_
    dup_count = len(dup_list)
    logging.info('Found %d duplicate file sets by mime', dup_count)
    '''

    logging.info( 'Pass 2/2' )
    dup_list_ = []
    for i, d_list in enumerate( dup_list ):
        logging.debug( 'Processing %s/%s', i + 1, dup_count )
        dup_list_.extend( hash_walk( d_list, args.hashblocks ) )

    dup_list = dup_list_
    dup_count = len( dup_list )
    logging.info( 'Found %d duplicate file sets by hash', dup_count )

    for d in dup_list:
        size_bytes = os.path.getsize( d[0] )
        d.insert( 0, bytes_in_unit_str( size_bytes * len( d ) ) )
        d.insert( 0, bytes_in_unit_str( size_bytes ) )

    out_path = conpath( args.out )
    logging.info( 'Writing to file: %s', out_path )
    with open( out_path, 'wb' ) as f:
        csv_writer = csv.writer( f )
        csv_writer.writerow( ['file size', 'total size'] )
        csv_writer.writerows( dup_list )


def validate_paths( path_list ):
    path_list = sorted( set( map( conpath, path_list ) ) )
    for i in xrange( len( path_list ) - 1, -1, -1 ):
        for j in xrange( len( path_list ) - 1, -1, -1 ):
            if i == j:
                continue

            if path_list[i].startswith( path_list[j] ):
                del path_list[i]
                break

    logging.info( 'Resolved paths: \n\t%s', '\n\t'.join( path_list ) )
    return path_list


def size_walk( path_list, sizemin, sizemax ):
    #logging.debug( 'sizemin: %s', sizemin )
    #logging.debug( 'sizemax: %s', sizemax )
    check_size = lambda x: True

    min_ = isinstance( sizemin, long ) and sizemin > 0
    max_ = isinstance( sizemax, long ) and sizemax > 0
    if min_ and max_:
        check_size = lambda x: ( x >= sizemin and x <= sizemax )
    elif min_:
        check_size = lambda x: x >= sizemin
    elif max_:
        check_size = lambda x: x <= sizemax

    size_dict = defaultdict( set )
    for p in path_list:
        for dirpath, sub_dir_list, file_list in os.walk( p ):
            logging.debug( 'Processing %s', dirpath )
            for i in xrange( len( sub_dir_list ) - 1, -1, -1 ):
                if RE_IGNORE.search( sub_dir_list[i] ) is None:
                    continue
                del sub_dir_list[i]
            # logging.debug('\n\t%s', '\n\t'.join(sub_dir_list))

            for i in xrange( len( file_list ) - 1, -1, -1 ):
                if RE_IGNORE.search( file_list[i] ) is not None:
                    del file_list[i]
                    continue
                file_path = conpath( os.path.join( dirpath, file_list[i] ) )
                if not os.path.isfile( file_path ):
                    del file_list[i]
                    continue
                size_bytes = os.path.getsize( file_path )
                #logging.debug('- %s: %s (%s bytes)', file_path, bytes_in_unit_str(size_bytes), size_bytes)
                # raw_input()
                if not check_size( size_bytes ):
                    # logging.debug('skipping')
                    continue
                size_dict[size_bytes].add( file_path )

    dup_list = []
    for size_bytes in sorted( size_dict ):
        if len( size_dict[size_bytes] ) > 1:
            dup_list.append( sorted( size_dict[size_bytes] ) )

    return dup_list


def mime_walk( path_list ):
    mime_dict = defaultdict( list )
    count = len( path_list )
    for i, p in enumerate( path_list ):
        logging.debug( '\t%s/%s', i + 1, count )
        try:
            mime_type = magic.from_file( p, mime=True )
        except Exception as e:
            logging.warn( 'Error processing file: %s', p )
            # logging.exception(e)
            # return path_list
            # return []
            continue
        mime_dict[mime_type].append( p )

    dup_list = []
    for mime in sorted( mime_dict ):
        if len( mime_dict[mime] ) > 1:
            dup_list.append( mime_dict[mime] )

    return dup_list


def hash_walk( path_list, block_count=10 ):
    hash_dict = defaultdict( list )
    count = len( path_list )
    for i, p in enumerate( path_list ):
        logging.debug( '\t%s/%s', i + 1, count )
        try:
            hash_value = ioutil.file_hash( p, block_count=block_count )
        except Exception as e:
            logging.warn( 'Error processing file: %s', p )
            logging.exception( e )
            # return path_list
            # return []
            continue
        hash_dict[hash_value].append( p )

    dup_list = []
    for hash_value in hash_dict:
        if len( hash_dict[hash_value] ) > 1:
            dup_list.append( hash_dict[hash_value] )

    return dup_list

if __name__ == '__main__':
    logging.basicConfig( level=logging.DEBUG )
    main()
