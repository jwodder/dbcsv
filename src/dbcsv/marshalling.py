# Marshalling (type → str) converters are resolved as follows:
# - If there is a converter registered for the SQLAlchemy column type, use that
# - [Don't bother checking the column type's `python_type` here; it'll either
#   be the same as the type of the raw Python value, in which case it's
#   redundant, or it won't, in which case using it would be wrong]
# - Otherwise, marshal based on the type of the raw Python value

# Unmarshalling (str → type) converters are resolved as follows:
# - If there is a converter registered for the SQLAlchemy column type, use that
# - Otherwise, if the column type's `python_type` attribute resolves, unmarshal
#   based on that
# - Otherwise, error

from   ast      import literal_eval
import base64
from   datetime import date, datetime, time, timedelta
from   decimal  import Decimal
from   enum     import Enum
import json
import re
from   backports.datetime_fromisoformat import MonkeyPatch
import sqlalchemy as S

MonkeyPatch.patch_fromisoformat()

NULL_TOKEN = r'\N'

coltype_marshallers = {}
pytype_marshallers = {}

coltype_unmarshallers = {}
pytype_unmarshallers = {}

def register_column_type(coltype, marshaller, unmarshaller):
    try:
        is_coltype = issubclass(coltype, S.types.TypeEngine)
    except TypeError:
        is_coltype = False
    if not is_coltype:
        raise TypeError('coltype must be a subclass of sqlalchemy.types.TypeEngine')
    coltype_marshallers[coltype] = marshaller
    coltype_unmarshallers[coltype] = unmarshaller

def register_python_type(pytype, marshaller, unmarshaller):
    pytype_marshallers[pytype] = marshaller
    pytype_unmarshallers[pytype] = unmarshaller

def marshal_object(table, obj):
    """
    Convert a `Mapping` (such as a `~sqlalchemy.engine.RowProxy`) to a `dict`
    in which all values are `str`.
    """
    return {k: marshal_field(v, table.columns[k].type) for k,v in obj.items()}

def unmarshal_object(table, obj):
    """
    Convert a `Mapping` in which all values are `str` (such as a row returned
    from `csv.DictReader`) to a `dict` in which the values match the types used
    for the columns of the same names in ``table``.
    """
    return {k: unmarshal_field(v, table.columns[k].type) for k,v in obj.items()}

def marshal_field(value, coltype):
    if value is None:
        return NULL_TOKEN
    if type(coltype) in coltype_marshallers:
        converter = coltype_marshallers[type(coltype)]
        return converter(value, coltype)
    elif type(value) in pytype_marshallers:
        converter = pytype_marshallers[type(value)]
        return converter(value)
    else:
        raise ValueError('No marshaller registered for type '
                         + repr(type(coltype)))

def unmarshal_field(s, coltype):
    if s == NULL_TOKEN:
        return None
    if type(coltype) in coltype_unmarshallers:
        converter = coltype_unmarshallers[type(coltype)]
        return converter(s, coltype)
    try:
        pytype = coltype.python_type
    except Exception:
        pass
    else:
        if pytype in pytype_unmarshallers:
            converter = pytype_unmarshallers[pytype]
            return converter(s)
    raise ValueError('No unmarshaller registered for type '+repr(type(coltype)))

def marshal_str(s):
    m = re.fullmatch(r'(\x5C+)N', s)
    if m:
        return m.group(1) * 2 + 'N'
    else:
        return s

def unmarshal_str(s):
    m = re.fullmatch(r'(\x5C+)N', s)
    if m:
        return '\\' * (len(m.group(1)) // 2) + 'N'
    else:
        return s

def marshal_bytes(blob):
    return base64.b64encode(blob).decode('us-ascii')

def unmarshal_bytes(s):
    return base64.b64decode(s)

def marshal_timedelta(td):
    return str(td.total_seconds())

def unmarshal_timedelta(s):
    return timedelta(seconds=float(s))

def marshal_enum(value, coltype):
    assert isinstance(coltype, S.Enum)
    if issubclass(coltype.python_type, Enum):
        assert isinstance(value, Enum)
        return marshal_str(value.name)
    else:
        assert isinstance(value, str)
        return marshal_str(value)

def unmarshal_enum(s, coltype):
    assert isinstance(coltype, S.Enum)
    if issubclass(coltype.python_type, Enum):
        return coltype.python_type[unmarshal_str(s)]
    else:
        return unmarshal_str(s)

# Distinguishing between SQL `NULL` and JSON `null` seems to be a lost cause,
# as both values are retrieved from the database (when that database is
# PostgreSQL, at least) as Python `None`.  Unmarshalling `\N` and `null` into
# `S.null()` and `S.JSON.NULL`, respectively, isn't really workable either, as
# `S.null()` is a column expression and thus we can't check whether it's equal
# to itself in a test.

def marshal_json(value, coltype):
    return json.dumps(value)

def unmarshal_json(s, coltype):
    return json.loads(s)

def marshal_pickle(value, coltype):
    return base64.b64encode(
        coltype.pickler.dumps(value, protocol=coltype.protocol)
    ).decode('us-ascii')

def unmarshal_pickle(s, coltype):
    return coltype.pickler.loads(base64.b64decode(s))

def marshal_array(value, coltype):
    def marshal(x):
        if isinstance(x, (list, tuple)):
            return type(x)(map(marshal, x))
        else:
            return marshal_field(x, coltype.item_type)
    return str(marshal(value))

def unmarshal_array(s, coltype):
    def unmarshal(x):
        if isinstance(x, (list, tuple)):
            return type(x)(map(unmarshal, x))
        else:
            return unmarshal_field(x, coltype.item_type)
    return unmarshal(literal_eval(s))

register_python_type(str, marshal_str, unmarshal_str)
register_python_type(int, str, int)
register_python_type(float, str, float)
register_python_type(Decimal, str, Decimal)
### TODO: The `bool` functions should raise ValueError on invalid input:
register_python_type(bool, 'ft'.__getitem__, {'f': False, 't': True}.__getitem__)
register_python_type(bytes, marshal_bytes, unmarshal_bytes)
register_python_type(datetime, datetime.isoformat, datetime.fromisoformat)
register_python_type(date, date.isoformat, date.fromisoformat)
register_python_type(time, time.isoformat, time.fromisoformat)
register_python_type(timedelta, marshal_timedelta, unmarshal_timedelta)

register_column_type(S.Enum, marshal_enum, unmarshal_enum)
register_column_type(S.JSON, marshal_json, unmarshal_json)
register_column_type(S.PickleType, marshal_pickle, unmarshal_pickle)
register_column_type(S.ARRAY, marshal_array, unmarshal_array)
