"""Constants for the OT-Croissant package."""

import mlcroissant as mlc

TYPE_DICT = {
    'string': mlc.DataType.TEXT,
    'boolean': mlc.DataType.BOOL,
    'long': mlc.DataType.FLOAT,
    'double': mlc.DataType.FLOAT,
    'integer': mlc.DataType.INTEGER,
    'float': mlc.DataType.FLOAT,
    'date': mlc.DataType.DATE,
}
