- Write a command-line interface for dumping & loading databases modeled via
  reflection
- When marshalling or unmarshalling a field fails, include the file/table, line
  number, and column name in the error message
- Rethink what the first argument to the `load*` and `dump*` functions should
  be: an Engine?  Connection?  Transaction?  Session?
    - All `Connectable`s (`Engine` and `Connection`) should be accepted.  Also
      try to support `Session`s.
- Handle CSV entries with incorrect numbers of fields
- Support the ORM (i.e., support being passed a `Session` and an ORM class
  rather than a connection and a table)
- Support dumping a `ResultProxy` to a file (accompanied by an optional table
  or column name -> `Column`/column type mapping?)
- `JSON` type: Try unmarshalling `\N` and `null` into `S.null()` and
  `S.JSON.NULL` anyway?
