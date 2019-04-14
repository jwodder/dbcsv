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

# Marshalling is done based on the type of the value's Python representation.
marshallers = {}
unmarshallers = {}

def register_type(typecls, marsher, unmarsher):
    marshallers[typecls] = marsher
    unmarshallers[typecls] = unmarsher

def marshal_field(value):
    if value is None:
        return NULL_TOKEN
    try:
        converter = marshallers[type(value)]
    except KeyError:
        if isinstance(value, Enum):
            return marshal_str(value.name)
        else:
            raise ValueError('No marshaller registered for type '
                             + repr(type(value)))
    else:
        return converter(value)

def unmarshal_field(s, coltype):
    if s == NULL_TOKEN:
        return None
    try:
        converter = unmarshallers[coltype]
    except KeyError:
        if issubclass(coltype, Enum):
            return coltype[unmarshal_str(s)]
        else:
            raise ValueError('No unmarshaller registered for type '
                             + repr(coltype))
    else:
        return converter(s)

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

register_type(str, marshal_str, unmarshal_str)
register_type(int, str, int)
register_type(float, str, float)
register_type(Decimal, str, Decimal)
### TODO: The `bool` functions should raise ValueError on invalid input:
register_type(bool, 'ft'.__getitem__, {'f': False, 't': True}.__getitem__)
register_type(bytes, marshal_bytes, unmarshal_bytes)
register_type(datetime, datetime.isoformat, datetime.fromisoformat)
register_type(date, date.isoformat, date.fromisoformat)
register_type(time, time.isoformat, time.fromisoformat)
register_type(timedelta, marshal_timedelta, unmarshal_timedelta)
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
    return {k: marshal_field(v) for k,v in obj.items()}

def unmarshal_object(table, obj):
    """
    Convert a `Mapping` in which all values are `str` (such as a row returned
    from `csv.DictReader`) to a `dict` in which the values match the types used
    for the columns of the same names in ``table``.
    """
    return {
        k: unmarshal_field(v, table.columns[k].type.python_type)
        for k,v in obj.items()
    }
