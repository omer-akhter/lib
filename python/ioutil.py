import os


def auth_user( user=None, pass_=None ):
    import getpass
    if user is None:
        user = raw_input( 'User: ' )
    if pass_ is None:
        pass_ = getpass( 'Password: ' )
    return ( user, pass_ )

path_abs = lambda x: os.path.normpath( os.path.abspath( x ) )
path_con = lambda x: os.path.realpath( path_abs( x ) )


def file_contents( path ):
    with open( path ) as _file:
        return _file.read()


#===============================================================================
# Source: http://stackoverflow.com/a/379535
#=========================================================================

def is_exe( fpath ):
    return os.path.exists( fpath ) and os.access( fpath, os.X_OK )


def which( program ):
    def ext_candidates( fpath ):
        yield fpath
        for ext in os.environ.get( 'PATHEXT', '' ).split( os.pathsep ):
            yield fpath + ext

    fpath, _ = os.path.split( program )
    if fpath:
        if is_exe( program ):
            return program

    else:
        for path in os.environ['PATH'].split( os.pathsep ):
            exe_file = os.path.join( path, program )
            for candidate in ext_candidates( exe_file ):
                if is_exe( candidate ):
                    return candidate

    return None

#------------------------------------------------------------------------------
