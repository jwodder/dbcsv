"""
Dump & load databases as CSV

Visit <https://github.com/jwodder/dbcsv> for more information.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'dbcsv@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/dbcsv'

import base64
import csv
from   datetime import date, datetime, time, timedelta
from   decimal  import Decimal
from   enum     import Enum
from   pathlib  import Path
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

def register_python_type(coltype, marshaller, unmarshaller):
    pytype_marshallers[coltype] = marshaller
    pytype_unmarshallers[coltype] = unmarshaller

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

### JSON
### ARRAY = list
### PickleType ?
### INET ?

def dumpdb(conn, metadata, dirpath):
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    for tbl in metadata.sorted_tables:
        with (dirpath / (tbl.name + '.csv')).open('w') as fp:
            dump_table(conn, tbl, fp)

def dump_table(conn, table, outfile):
    writer = csv.DictWriter(outfile, table.columns.keys())
    writer.writeheader()
    for entry in conn.execute(S.select([table])):
        writer.writerow(marshal_object(table, entry))

def loaddb(conn, metadata, dirpath):
    for tbl in metadata.sorted_tables:
        try:
            with (dirpath / (tbl.name + '.csv')).open('r') as fp:
                load_table(conn, tbl, fp)
        except FileNotFoundError:
            pass

def load_table(conn, table, infile):
    for row in csv.DictReader(infile):
        ### TODO: Should this use `executemany` instead?
        conn.execute(table.insert(values=unmarshal_object(table, row)))

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
