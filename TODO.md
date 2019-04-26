- Write a command-line interface for dumping & loading databases modeled via
  reflection
- When marshalling or unmarshalling a field fails, include the file/table, line
  number, and column name in the error message
- Handle CSV entries with incorrect numbers of fields
- Support the ORM (i.e., support being passed a `Session` and an ORM class
  rather than a connection and a table)
- Support dumping a `ResultProxy` to a file (accompanied by an optional table
  or column name -> `Column`/column type mapping?)
- `JSON` type: Try unmarshalling `\N` and `null` into `S.null()` and
  `S.JSON.NULL` anyway?
- Add docstrings
- Add a note to the documentation about the restrictions regarding JSON nulls
- Add a note to the documentation about the order that `loaddb()` loads tables
  in
- Document the exact formats that values are serialized in?
- Expand README description
- Test `loaddb()` and `dumpdb()` with both a string and `Path` as the `dirpath`
  argument
