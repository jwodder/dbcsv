- Write a command-line interface for dumping & loading databases modeled via
  reflection
- When marshalling or unmarshalling a field fails, include the file/table, line
  number, and column name in the error message
- Rethink what the first argument to the `load*` and `dump*` functions should
  be: an Engine?  Connection?  Transaction?  Session?
- Support marshalling based on the column type (just for those types without
  `.python_type` properties?)
- Handle CSV entries with incorrect numbers of fields
