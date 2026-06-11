"""Constants for the OT-Croissant package."""

import mlcroissant as mlc

# Maps PySpark typeName() strings to their Croissant DataType equivalents.
TYPE_DICT = {
    # Text / boolean
    'string': mlc.DataType.TEXT,
    'boolean': mlc.DataType.BOOL,
    # Signed integers — ordered by width
    'byte': mlc.DataType.INT8,
    'short': mlc.DataType.INT16,
    'integer': mlc.DataType.INT32,
    'long': mlc.DataType.INT64,
    # Floating-point — ordered by width
    'float': mlc.DataType.FLOAT32,
    'double': mlc.DataType.FLOAT64,
    'decimal': mlc.DataType.FLOAT64,  # arbitrary-precision; best approximation
    # Date / time
    'date': mlc.DataType.DATE,
    'timestamp': mlc.DataType.DATETIME,
    'timestamp_ntz': mlc.DataType.DATETIME,
}
