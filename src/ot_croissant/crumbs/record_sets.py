"""Class to create the croissant recordset metadata for the Open Targets Platform."""

import mlcroissant as mlc
from ot_croissant.constants import typeDict
import pyarrow.parquet as pq
from pyarrow.lib import DataType
import pyarrow as pa


class PlatformOutputRecordSets:
    """Class to  in the Open Targets Platform data."""

    record_sets: list[mlc.RecordSet]

    def __init__(self):
        self.record_sets = []
        super().__init__()

    def get_metadata(self) -> list[mlc.RecordSet]:
        """Return the distribution metadata."""
        return self.record_sets

    def add_assets_from_paths(self, paths: list[str]):
        """Add files from a list to the distribution."""
        for path in paths:
            self.record_sets.append(self.get_fileset_recordset(path))
        return self

    def get_fileset_recordset(self, path: str) -> mlc.RecordSet:
        """Returns the recordset for a fileset."""
        id = path.split("/")[-1]
        print(id)
        return mlc.RecordSet(id=id, name=id, fields=self.get_fileset_fields(path))
        # return mlc.RecordSet(id=id, name=id)

    @staticmethod
    def subfield_parser(fileset_id: str, field: pa.Field) -> list[mlc.Field]:
        subfields = []
        for i in range(field.type.num_fields):
            subfield = field.type.field(i)
            print(subfield.name)
            if field.type.num_fields == 0:
                subfields.append(
                    mlc.Field(
                        id=fileset_id + "/" + field.name + "/" + subfield.name,
                        name=subfield.name,
                        description=f"PLACEHOLDER for {field.name} description",
                        data_types=mlc.DataType.TEXT,
                    )
                )
        return subfields

    @staticmethod
    def column_parser(distribution_id: str, field: pa.Field) -> mlc.Field:
        """Parse the column name and data type to create a field."""
        # print(type(pa_dtype) == pa.ListType)
        # print(field.type.num_fields)
        # if pa_dtype not in typeDict:
        #     print("Skipping")
        #     continue
        if field.type.num_fields == 0:
            print("[ADDED]")
            return mlc.Field(
                id=distribution_id + "/" + field.name,
                name=field.name,
                description=f"PLACEHOLDER for {field.name} description",
                data_types=mlc.DataType.TEXT,
                source=mlc.Source(
                    file_set=distribution_id + "-fileset",
                    extract=mlc.Extract(column=field.name),
                ),
            )
        else:
            PlatformOutputRecordSets.column_parser()
            pass
            # if type(field.type) is pa.ListType:
            #     print(f"Num fields: {field.type.num_fields}")
            #     return mlc.Field(
            #         id=distribution_id + "/" + field.name,
            #         name=field.name,
            #         repeated=True,
            #         description=f"PLACEHOLDER for {field.name} description",
            #         source=mlc.Source(
            #             file_set=distribution_id + "-fileset",
            #             extract=mlc.Extract(column=field.name),
            #         ),
            #     )

    @staticmethod
    def get_fileset_fields(path: str) -> list[mlc.Field]:
        """Returns the fields for a fileset."""
        fields = []
        id = path.split("/")[-1]
        # schema = scan_parquet(path).collect_schema().to_python()
        schema = pq.ParquetDataset(path).schema
        for field in schema:
            print(
                f"ID: {id}/{field.name} Type: {str(field.type)} NumFields: {field.type.num_fields}"
            )
            if field.type.num_fields == 0:
                fields.append(
                    PlatformOutputRecordSets.column_parser(
                        distribution_id=id, field=field
                    )
                )
        return fields

    #     mlc.RecordSet(
    #         id="jsonl",
    #         name="jsonl",
    #         # Each record has one or many fields...
    #         fields=[
    #             # Fields can be extracted from the FileObjects/FileSets.
    #             mlc.Field(
    #                 id="jsonl/context",
    #                 name="context",
    #                 description="",
    #                 data_types=mlc.DataType.TEXT,
    #                 source=mlc.Source(
    #                     file_set="jsonl-files",
    #                     # Extract the field from the column of a FileObject/FileSet:
    #                     extract=mlc.Extract(column="context"),
    #                 ),
    #             ),
    #             mlc.Field(
    #                 id="jsonl/completion",
    #                 name="completion",
    #                 description="The expected completion of the promt.",
    #                 data_types=mlc.DataType.TEXT,
    #                 source=mlc.Source(
    #                     file_set="jsonl-files",
    #                     extract=mlc.Extract(column="completion"),
    #                 ),
    #             ),
    #             mlc.Field(
    #                 id="jsonl/task",
    #                 name="task",
    #                 description=(
    #                     "The machine learning task appearing as the name of the"
    #                     " file."
    #                 ),
    #                 data_types=mlc.DataType.TEXT,
    #                 source=mlc.Source(
    #                     file_set="jsonl-files",
    #                     extract=mlc.Extract(
    #                         file_property=mlc._src.structure_graph.nodes.source.FileProperty.filename
    #                     ),
    #                     # Extract the field from a regex on the filename:
    #                     transforms=[mlc.Transform(regex="^(.*)\.jsonl$")],
    #                 ),
    #             ),
    #         ],
    #     )
    # ]
