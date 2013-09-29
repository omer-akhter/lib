# Source: http://code.activestate.com/recipes/473888-lazy-module-imports/

# Copyright rPath, Inc., 2006
# Available under the python license
""" Defines an on-demand importer that only actually loads modules when their
    attributes are accessed.  NOTE: if the ondemand module is viewed using
    introspection, like dir(), isinstance, etc, it will appear as a
    ModuleProxy, not a module, and will not have the correct attributes.
    Barring introspection, however, the module will behave as normal.
"""

'''
Changes:
 - Added changes suggested by Tim Mitchell in the comments (at source)
 - Added a few of my own changes to make it more Object-Oriented
 - Renamed and file variable to file_
 - Formatted using autopep8
 - Added space before and after parenthesis
'''

import imp
import sys
import types


__all__ = ['OnDemandImporter']


def makeImportedModule( name, pathname, desc, scope ):
    """ Returns a ModuleProxy that has access to a closure w/
        information about the module to load, but is otherwise
        empty.  On an attempted access of any member of the module,
        the module is loaded.
    """

    def _loadModule():
        """ Load the given module, and insert it into the parent
            scope, and also the original importing scope.
        """

        mod = sys.modules.get( name, None )
        if mod is None or not isinstance( mod, types.ModuleType ):
            try:
                file_ = open( pathname, 'U' )
            except:
                file_ = None

            try:
                mod = imp.load_module( name, file_, pathname, desc )
            finally:
                if file_ is not None:
                    file_.close()

            sys.modules[name] = mod

        scope[name] = mod

        frame = sys._getframe( 2 )
        global_scope = frame.f_globals
        local_scope = frame.f_locals

        # check to see if this module exists for any part of the name
        # we are importing, e.g. if you are importing foo.bar.baz,
        # look for foo.bar.baz, bar.baz, and baz.
        moduleParts = name.split( '.' )
        names = [ '.'.join( moduleParts[-x:] )
                  for x in range( len( moduleParts ) ) ]
        for modulePart in names:
            if modulePart in local_scope:
                if local_scope[modulePart].__class__.__name__ == 'ModuleProxy':
                    # FIXME: this makes me cringe, but I haven't figured out a
                    # better way to ensure that the module proxy we're
                    # looking at is actually a proxy for this module
                    if pathname in repr( local_scope[modulePart] ):
                        local_scope[modulePart] = mod
            if modulePart in global_scope:
                if global_scope[modulePart].__class__.__name__ == 'ModuleProxy':
                    if pathname in repr( global_scope[modulePart] ):
                        global_scope[modulePart] = mod

        return mod

    class ModuleProxy( object ):
        __slots__ = []
        # we don't add any docs for the module in case the
        # user tries accessing '__doc__'

        def __hasattr__( self, key ):
            mod = _loadModule()
            return hasattr( mod, key )

        def __getattr__( self, key ):
            mod = _loadModule()
            return getattr( mod, key )

        def __setattr__( self, key, value ):
            mod = _loadModule()
            return setattr( mod, key, value )

        def __repr__( self ):
            return "<moduleProxy '%s' from '%s'>" % ( name, pathname )

    return ModuleProxy()


class OnDemandLoader( object ):

    """ The loader takes a name and info about the module to load and
        "loads" it - in this case returning loading a proxy that
        will only load the class when an attribute is accessed.
    """
    def __init__( self, name, file_, pathname, desc, scope ):
        self.file_ = file_
        self.name = name
        self.pathname = pathname
        self.desc = desc
        self.scope = scope

    def load_module( self, fullname ):
        if fullname in __builtins__:
            try:
                mod = imp.load_module( self.name, self.file_,
                                       self.pathname, self.desc )
            finally:
                if self.file_:
                    self.file_.close()
            sys.modules[fullname] = mod
        else:
            if self.file_:
                self.file_.close()
            mod = makeImportedModule( self.name, self.pathname, self.desc,
                                      self.scope )
            sys.modules[fullname] = mod
        return mod


class OnDemandImporter( object ):

    """ The on-demand importer imports a module proxy that
        inserts the desired module into the calling scope only when
        an attribute from the module is actually used.
    """

    def __init__( self, *skip ):
        self._skip = set( skip )

    def find_module( self, fullname, path=None ):
        if set( fullname.split( '.' ) ) & self._skip:
            return None

        origName = fullname
        if not path:
            mod = sys.modules.get( fullname, False )
            if mod is None or mod and isinstance( mod, types.ModuleType ):
                return mod

        frame = sys._getframe( 1 )
        global_scope = frame.f_globals
        # this is the scope in which import <fullname> was called

        if '.' in fullname:
            head, fullname = fullname.rsplit( '.', 1 )

            # this import protocol works such that if I am going to be
            # able to import fullname, then everything in front of the
            # last . in fullname must already be loaded into sys.modules.
            mod = sys.modules.get( head, None )
            if mod is None:
                return None

            if hasattr( mod, '__path__' ):
                path = mod.__path__

        try:
            file_, pathname, desc = imp.find_module( fullname, path )
            return OnDemandLoader( origName, file_, pathname, desc, global_scope )
        except ImportError:
            # don't return an import error.  That will stop
            # the automated search mechanism from working.
            return None

    @staticmethod
    def lazy_reload( module ):
        if isinstance( module, types.ModuleType ):
            OnDemandImporter._real_reload( module )

    @classmethod
    def install( cls, *skip ):
        # print '__builtins__:', __builtins__
        reload_ = __builtins__['reload']
        if reload_ != cls.lazy_reload:
            cls._real_reload = reload_

        cls._instance = OnDemandImporter( *skip )
        sys.meta_path.append( cls._instance )
        __builtins__['reload'] = cls.lazy_reload

    @classmethod
    def uninstall( cls ):
        try:
            sys.meta_path.remove( cls._instance )
        except ValueError:
            pass
        else:
            try:
                __builtins__['reload'] = cls._real_reload
                del cls._real_reload
            except:
                pass
