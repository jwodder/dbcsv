"""
Dump & load databases as CSV

``dbcsv`` is a Python library for vendor-independent loading & dumping of SQL
database tables as CSV files, including automatic serialization &
deserialization of nontrivial types like timestamps and JSON objects.

Visit <https://github.com/jwodder/dbcsv> for more information.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'dbcsv@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/dbcsv'

from .load_dump   import dump_table, dumpdb, load_table, loaddb
from .marshalling import register_column_type, register_python_type

__all__ = [
    'dump_table',
    'dumpdb',
    'load_table',
    'loaddb',
    'register_column_type',
    'register_python_type',
]
