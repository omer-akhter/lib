import argparse
import logging
import os

from ioutil import path_con, path_abs


LOGGING_CHOICES = (
    ( 'q', None ),
    ( 'quiet', None ),
    ( 'd', logging.DEBUG ),
    ( 'debug', logging.DEBUG ),
    ( 'i', logging.INFO ),
    ( 'info', logging.INFO ),
    ( 'w', logging.WARNING ),
    ( 'warn', logging.WARNING ),
    ( 'e', logging.ERROR ),
    ( 'error', logging.ERROR ),
    ( 'c', logging.CRITICAL ),
    ( 'critical', logging.CRITICAL ),
)


class PathType( object ):

    """Factory for creating path object types

    Instances of PathType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - is_directory -- True if path is a directory.
        - check_exists -- True if requires exist.
        - check_read -- True if read access is required.
        - check_write -- True if write access is required.
        - canonical --
        - absolute --
    """

    def __init__( self, canonical=False, absolute=False, check_exists=False,
                  check_not_exists=False, check_read=False, check_write=False,
                  is_directory=None ):
        self._canonical = canonical
        self._absolute = absolute
        self._check_write = check_write
        self._check_read = check_read
        self._check_exists = check_exists
        self._check_not_exists = check_not_exists
        self._is_directory = is_directory

    def __call__( self, path_str ):
        self._path_str_org = path_str

        if self._canonical:
            path_str = path_con( path_str )
        elif self._absolute:
            path_str = path_abs( path_str )

        self._path_str = path_str
        self._exists = os.path.exists( path_str )
        self._r_ok = os.access( path_str, os.R_OK )
        self._w_ok = os.access( path_str, os.W_OK )
        self._isdir = os.path.isdir( path_str )
        self._isfile = os.path.isfile( path_str )
        self._islink = os.path.islink( path_str )

        if self._check_read:
            if not self._r_ok:
                raise ValueError(
                    'permission to read from path %s are not available' %
                    path_str )
        elif self._check_exists:
            if not self._exists:
                raise ValueError( 'path %s does not exist' % path_str )
        elif self._check_not_exists:
            if self._exists:
                raise ValueError( 'path %s exists' % path_str )
        if self._check_write:
            if self._exists:
                if not self._w_ok:
                    raise ValueError(
                        'permission to write on path %s are not available' %
                        path_str )
            else:
                existing_path = path_str
                while existing_path and not os.path.exists( existing_path ):
                    existing_path, _ = os.path.split( existing_path )

                if not ( os.path.exists( existing_path ) and os.access( path_str, os.W_OK ) ):
                    raise ValueError(
                        'permission to write on path %s are not available' %
                        path_str )

        if self._is_directory and not self._isdir:
            raise ValueError( 'path %s is not a directory' % path_str )
        elif self._is_directory == False and self._isdir:
            raise ValueError( 'path %s is a directory' % path_str )

        return path_str

    def __repr__( self, *args, **kwargs ):
        return self.__class__.__name__


class LogType( object ):

    """Factory for creating log object types

    Instances of LogType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.
    """

    def __init__( self, set_=True,
                  format_='%(levelname)s: %(message)s' ):
        self._set = set_
        self._format = format_

    def __call__( self, val_str ):
        self._val_str = val_str
        try:
            self._log_level = filter(
                lambda x_y1: x_y1[0] == val_str,
                LOGGING_CHOICES )[0][-1]
        except:
            raise ValueError( 'invalid value %s' % val_str )

        if self._set:
            if self._log_level is not None:
                logging.basicConfig(
                    format=self._format,
                    level=self._log_level )
            else:
                logging.disable( logging.DEBUG )

        return self._log_level

    def __repr__( self, *args, **kwargs ):
        repr_str = self.__class__.__name__
        try:
            repr_str += '(%s)' % filter(
                lambda x_y: x_y[0] == self._val_str,
                LOGGING_CHOICES )[-1][0]
        except:
            pass
        return repr_str


class ArgParser2( argparse.ArgumentParser ):

    def __init__( self, prog=None, usage=None, description=None, epilog=None,
                  version=None, parents=None, formatter_class=argparse.HelpFormatter,
                  prefix_chars='-', fromfile_prefix_chars='@', argument_default=None,
                  conflict_handler='error', add_help=True ):

        if parents is None:
            parents = []

        argparse.ArgumentParser.__init__(
            self, prog, usage, description, epilog, version,
            parents, formatter_class, prefix_chars, fromfile_prefix_chars,
            argument_default, conflict_handler, add_help )

    def convert_arg_line_to_args( self, arg_line ):
        arg_line = arg_line.strip()
        if not arg_line or arg_line.startswith( '#' ):
            return
        for arg in arg_line.split():
            if not arg.strip():
                continue
            yield arg
