### TODO: Rethink what the first argument to the load* and dump* functions
### should be: an Engine?  Connection?  Transaction?  Session?

# Marshalling is done based on the type of the value's Python representation.

### TODO: Support marshalling based on the column type (just for those types
### without .python_type properties?)

__python_requires__ = '~= 3.5'
import base64
import csv
from   pathlib import Path
import re
import sqlalchemy as S

NULL_TOKEN = r'\N'

marshallers = {}
unmarshallers = {}

def register_type(typecls, marsher, unmarsher):
    marshallers[typecls] = marsher
    unmarshallers[typecls] = unmarsher

def marshal(value):
    if value is None:
        return NULL_TOKEN
    try:
        converter = marshallers[type(value)]
    except KeyError:
        raise ValueError('No marshaller registered for type '+repr(type(value)))
    else:
        return converter(value)

def unmarshal(s, coltype):
    if s == NULL_TOKEN:
        return None
    try:
        converter = unmarshallers[coltype]
    except KeyError:
        raise ValueError('No unmarshaller registered for type ' + repr(coltype))
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

register_type(str, marshal_str, unmarshal_str)
register_type(int, str, int)
register_type(bool, 'ft'.__getitem__, {'f': False, 't': True}.__getitem__)
register_type(bytes, marshal_bytes, unmarshal_bytes)
### datetime etc.
### enums
### INET?


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
        writer.writerow({k: marshal(v) for k,v in entry.items()})

def loaddb(conn, metadata, dirpath):
    for tbl in metadata.sorted_tables:
        try:
            with (dirpath / (tbl.name + '.csv')).open('r') as fp:
                load_table(conn, tbl, fp)
        except FileNotFoundError:
            pass

def load_table(conn, table, infile):
    for row in csv.DictReader(infile):
        conn.execute(
            table.insert(values={
                k: unmarshal(v, table.columns[k].type.python_type)
                for k,v in row.items()
            })
        )