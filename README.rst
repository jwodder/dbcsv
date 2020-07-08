.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP — Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://travis-ci.com/jwodder/dbcsv.svg?branch=master
    :target: https://travis-ci.com/jwodder/dbcsv

.. image:: https://codecov.io/gh/jwodder/dbcsv/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/dbcsv

.. image:: https://img.shields.io/github/license/jwodder/dbcsv.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/jwodder

`GitHub <https://github.com/jwodder/dbcsv>`_
| `Issues <https://github.com/jwodder/dbcsv/issues>`_

``dbcsv`` is a Python library for vendor-independent loading & dumping of SQL
database tables as CSV files, including automatic serialization &
deserialization of nontrivial types like timestamps and JSON objects.


Installation
============
``dbcsv`` requires Python 3.5 or higher.  Just use `pip <https://pip.pypa.io>`_
for Python 3 (You have pip, right?) to install ``dbcsv`` and its dependencies::

    python3 -m pip install git+https://github.com/jwodder/dbcsv.git


Example
=======

::

    import sqlalchemy as sa
    import dbcsv

    metadata = sa.MetaData()
    # Define your tables on the metadata like normal
    # ...

    engine = sa.create_engine(INSERT_DB_URL_HERE)
    conn = engine.connect()

    # Load CSVs into database:
    dbcsv.loaddb(conn, metadata, '/path/to/dump/directory')

    # Do data manipulation stuff

    # Dump database into CSVs:
    dbcsv.dumpdb(conn, metadata, '/dump/directory/path')


API
===

Loading & Dumping CSVs
----------------------

``dumpdb(conn: sqlalchemy.engine.Connectable, metadata: sqlalchemy.schema.MetaData, dirpath: os.PathLike)``
   Dump the contents of each table in ``metadata`` to a CSV file in directory
   ``dirpath`` named ``{table.name}.csv``.  If ``dirpath`` does not exist
   already, it is created.

``dump_table(conn: sqlalchemy.engine.Connectable, table: sqlalchemy.schema.Table, outfile)``
   Dump the contents of table ``table`` to the text-file-like object
   ``outfile`` as a CSV

``loaddb(conn: sqlalchemy.engine.Connectable, metadata: sqlalchemy.schema.MetaData, dirpath: os.PathLike)``
   Load the contents of each ``{table_name}.csv`` file in directory ``dirpath``
   into the corresponding table in the database

``load_table(conn: sqlalchemy.engine.Connectable, table: sqlalchemy.schema.Table, infile)``
   Load a text-file-like object ``infile`` containing CSV data into table
   ``table``


Supported Types
---------------

By default, ``dbcsv`` supports the following column types:

- Column types represented in Python as one of the following types:

  - ``bool`` (e.g., ``Boolean``) — serialized as ``f`` or ``t``
  - ``bytes`` (e.g., ``LargeBinary``) — serialized as base 64
  - ``datetime.date`` (e.g., ``Date``) — serialized in the format
    ``YYYY-MM-DD``
  - ``datetime.datetime`` (e.g., ``DateTime``) — serialized in the format
    ``YYYY-MM-DDTHH:MM:SS[.ssssss][+HH:MM]``
  - ``datetime.time`` (e.g., ``Time``) — serialized in the format
    ``HH:MM:SS[.ssssss][+HH:MM]``
  - ``datetime.timedelta`` (e.g., ``Interval``) — serialized as a
    floating-point number of seconds
  - ``decimal.Decimal`` (e.g., ``Numeric``)
  - ``float`` (e.g., ``Float``)
  - ``int`` (e.g., ``Integer``, ``BigInteger``, ``SmallInteger``)
  - ``str`` (e.g., ``String``, ``Text``, ``Unicode``, ``UnicodeText``)

- ``sqlalchemy.types.ARRAY(item_type)`` where ``item_type`` is also a supported
  column type — serialized as a ``repr`` of a Python list or tuple of strings
  of serialized values
- ``sqlalchemy.types.Enum`` (both string-based and ``enum.Enum``-based) —
  serialized as the enumeration label (for string-based) or the ``Enum``
  object's ``name`` attribute (for ``enum.Enum``-based)
- ``sqlalchemy.types.JSON`` — serialized as JSON
- ``sqlalchemy.types.PickleType`` — serialized as a pickled object in base 64

``None``\s/SQL ``NULL``\s are serialized as the string ``\N``.  In order to
avoid confusion with this value, any other value that would be serialized as
``\N`` is instead serialized as ``\\N`` (and ``\\N`` is likewise escaped as
``\\\\N`` etc.).


Registering New Types
---------------------
To register handlers for a new column type, use one of the following methods:

- Register handlers for the column type itself by calling
  ``dbcsv.register_column_type(coltype, marshaller, unmarshaller)`` where:

  - ``coltype`` is a subclass of ``sqlalchemy.types.TypeEngine``
  - ``marshaller`` is a function that takes a column value and an instance of
    ``coltype`` and returns a string
  - ``unmarshaller`` is a function that takes a string and an instance of
    ``coltype`` and returns a column value

- Register handlers for the Python type used to represent the column's values
  by calling ``dbcsv.register_python_type(pytype, marshaller, unmarshaller)``
  where:

  - ``pytype`` is a Python type.  In order for unmarshalling of the type to
    work, the column type's ``python_type`` attribute must evaluate to this
    type.
  - ``marshaller`` is a function that takes a Python value and returns a string
  - ``unmarshaller`` is a function that takes a string and returns a Python
    value

Marshalling & unmarshalling of ``None``/``NULL`` values is handled before
calling registered marshallers/unmarshallers, and so a marshaller will never be
passed a ``None``, and an unmarshaller will never be passed a ``r'\N'``.
Marshallers must take care to not return the string ``r'\N'`` unless they want
the value to be unmarshalled as ``None``; the functions
``dbcsv.marshalling.marshal_str()`` and ``dbcsv.marshalling.unmarshal_str()``
can be used to safely escape & unescape arbitrary strings in order to store an
actual ``r'\N'`` string or escaped form thereof.
