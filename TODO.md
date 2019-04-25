- Write a command-line interface for dumping & loading databases modeled via
  reflection
- When marshalling or unmarshalling a field fails, include the file/table, line
  number, and column name in the error message
- Rethink what the first argument to the `load*` and `dump*` functions should
  be: an Engine?  Connection?  Transaction?  Session?
    - All `Connectable`s (`Engine` and `Connection`) should be accepted.  Also
      try to support `Session`s.
- Support marshalling based on the column type (just for those types without
  `.python_type` properties?)
    - Possible way to resolve marshalling (type → str) converters:
        - If there is a converter registered for the SQLAlchemy column type,
          use that
        - [Don't bother checking the column type's `python_type` here; it'll
          either be the same as the type of the raw Python value, in which case
          it's redundant, or it won't, in which case using it would be wrong]
        - Otherwise, marshal based on the type of the raw Python value
    - Corresponding way to unmarshal (str → type):
        - If there is a converter registered for the SQLAlchemy column type,
          use that
        - Otherwise, if the column type's `python_type` attribute resolves,
          unmarshal based on that
        - Otherwise, error
- Handle CSV entries with incorrect numbers of fields
- Support the ORM (i.e., support being passed a `Session` and an ORM class
  rather than a connection and a table)
- Support dumping a `ResultProxy` to a file (accompanied by an optional table
  or column name -> `Column`/column type mapping?)
