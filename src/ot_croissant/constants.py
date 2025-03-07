import mlcroissant as mlc

# This Python code snippet defines a dictionary called `typeDict` that maps certain string keys to
# corresponding values from the `DataType` enumeration in the `mlcroissant` module. Here's what each
# key-value pair represents:
typeDict = {
    "string": mlc.DataType.TEXT,
    "boolean": mlc.DataType.BOOL,
    "long": mlc.DataType.FLOAT,
    "double": mlc.DataType.FLOAT,
    "integer": mlc.DataType.INTEGER,
    "float": mlc.DataType.FLOAT,
    "date": mlc.DataType.DATE,
}
