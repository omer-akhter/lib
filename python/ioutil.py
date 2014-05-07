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

#===============================================================================
# Source: https://stackoverflow.com/a/17782753
#=========================================================================


def file_hash( file_path, algo='md5', block_size=4096, block_count=None, hex_=False ):
    '''
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    '''
    import hashlib
    m = getattr( hashlib, algo )()
    with open( file_path, 'rb' ) as f:
        for chunk in iter( lambda: f.read( block_size ), b'' ):
            m.update( chunk )
            if block_count is None:
                continue
            if block_count == 0:
                break
            block_count -= 1
    if hex_:
        return m.hexdigest()
    return m.digest()
