import datetime
import hashlib
import time


def is_empty( value, do_strip=True ):
    if value is not None:
        if isinstance( value, ( unicode, str ) ):
            if do_strip:
                value = value.strip()
            return ( len( value ) == 0 )
        elif isinstance( value, ( tuple, list, dict, set ) ):
            return ( len( value ) == 0 )
        return False
    return True


def is_iterable( value ):
    if value is None:
        return False
    try:
        len( value )
        return True
    except:
        return False


def if_none( value, value_if_none ):
    if value is None:
        return value_if_none
    return value


def if_empty( value, value_if_empty ):
    if is_empty( value ):
        return value_if_empty
    return value


def long_or_none( numeric_value ):
    try:
        numeric_value = long( numeric_value )
        return numeric_value
    except:
        pass
    return None


def float_or_none( numeric_value ):
    try:
        numeric_value = float_or_none( numeric_value )
        return numeric_value
    except:
        pass
    return None


def type_name( value ):
    try:
        return type( value ).__name__
    except:
        return None


def snake_caseToCamelCase( snake_case ):
    return ''.join( ( word.capitalize() for word in snake_case.split( '_' ) ) )


def snake_caseTocamelCase( snake_case ):
    word_list = snake_case.split( '_' )
    return word_list[0] + ''.join( ( word.capitalize() for word in word_list[1:] ) )


def camelCaseTosnake_case( camelCase ):
    snake_case = camelCase[0].lower()
    for char in camelCase[1:]:
        if char.isupper():
            char = '_' + char.lower()
        snake_case += char

    return snake_case


def unix_timestamp( date_time_val=None ):
    if isinstance( date_time_val, ( datetime.date, datetime.datetime ) ):
        return long( time.mktime( date_time_val.timetuple() ) )
    return long( time.time() )


def date_time( ts=None, as_str=None ):
    if ts is None:
        ts = datetime.datetime.utcnow()

    if isinstance( ts, ( int, long ) ):
        ts = datetime.datetime.fromtimestamp( ts )

    if isinstance( ts, ( datetime.datetime, datetime.date ) ):
        if as_str:
            try:
                ts = ts.strftime( as_str )
            except:
                ts = ts.strftime( '%Y%m%d%H%M%S' )
    return ts


def time_delta( ts_old, ts_new=None, as_str=False, max_days=50 ):
    if ts_new is None:
        ts_new = datetime.datetime.now()

    _to_datetime = lambda ts: date_time(
        ts ) if isinstance( ts_old, ( long, int, float ) ) else ts

    ts_old = _to_datetime( ts_old )
    ts_new = _to_datetime( ts_new )

    if ( isinstance( ts_old, ( datetime.date, datetime.datetime ) ) and
         isinstance( ts_new, ( datetime.date, datetime.datetime ) ) ):
        ts_delta = ts_new - ts_old
        if as_str:
            if max_days is not None and max_days > 0 and ts_delta.days > max_days:
                ts_delta = 'long ago'
            else:
                ts_delta_str = ''
                if ts_delta.days > 0:
                    ts_delta_str += '%dd ' % ts_delta.days
                if ts_delta.seconds > 0:
                    mins = ts_delta.seconds / 60
                    secs = ts_delta.seconds % 60
                    hors = mins / 60
                    mins = mins % 60
                    if hors > 0:
                        ts_delta_str += '%dh ' % hors

                    if mins > 0:
                        ts_delta_str += '%dm ' % mins

                    if secs > 0:
                        ts_delta_str += '%ds' % secs

                ts_delta = ts_delta_str.strip()

        return ts_delta


def gen_hash( value, algo='md5' ):
    if not is_empty( value ):
        try:
            m = getattr( hashlib, algo )
            m = m()
            m.update( value )
            m = m.hexdigest()
            return m
        except:
            pass

    return None
