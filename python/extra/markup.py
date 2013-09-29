import logging

import yaml

import util


class MarkupObject( object ):

    @classmethod
    def load_yaml( cls, path ):
        logging.debug( 'loading %s', path )
        markup = None
        try:
            with open( path ) as f:
                markup = yaml.load( f )
        except IOError as e:
            logging.exception( e )
        except Exception as e:
            logging.exception( e )
        else:
            return cls.instance( path, markup )

    @classmethod
    def instance( cls, title, value ):
        value_type_name = util.type_name( value )
        class_name = 'Markup%sObject' % util.snake_caseToCamelCase(
            value_type_name )
        try:
            cls_ = globals()[class_name]
            if not issubclass( cls, cls_ ):
                return cls_( title, value )
        except:
            if value_type_name in ( 'int', 'long', 'float', 'complex', 'str', 'unicode' ):
                return value

        return cls( title, value )

    def __init__( self, title, value ):
        self.__title = title
        self._load_value( value )

    def _load_value( self, value ):
        self.__value = value

    @property
    def title( self ):
        return self.__title

    @property
    def raw_value( self ):
        return self.__value

    def serialize( self ):
        return ( self.title, self.raw_value )


class MarkupDictObject( dict, MarkupObject ):

    def __init__( self, title, value ):
        dict.__init__( self, value )
        MarkupObject.__init__( self, title, value )

    def _load_value( self, value ):
        MarkupObject._load_value( self, value )

        for k, v in self.iteritems():
            self[k] = v = MarkupObject.instance( k, v )
            setattr( self, k, v )

    def update2( self, **kwargs ):
        for k, v in kwargs.iteritems():
            self[k] = v = MarkupObject.instance( k, v )
            setattr( self, k, v )

    def serialize( self ):
        serialized = {}
        for k, v in self.iteritems():
            if isinstance( v, MarkupObject ):
                v = v.serialize()
            serialized[k] = v
        return serialized


class MarkupListObject( list, MarkupObject ):

    def __init__( self, title, value ):
        list.__init__( self, value )
        MarkupObject.__init__( self, title, value )

    def serialize( self ):
        serialized = []
        for v in self:
            if isinstance( v, MarkupObject ):
                v = v.serialize()
            serialized.append( v )
        return serialized
