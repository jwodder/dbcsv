import csv
from   pathlib      import Path
import sqlalchemy as S
from   .marshalling import marshal_object, unmarshal_object

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
