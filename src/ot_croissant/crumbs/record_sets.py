"""Class to create the croissant recordset metadata for the Open Targets Platform."""

from __future__ import annotations

from pyspark.sql import SparkSession, types as t
from pyspark.errors.exceptions.captured import AnalysisException
import mlcroissant as mlc
from ot_croissant.constants import typeDict
from ot_croissant.curation import DistributionCuration, RecordsetCuration
import logging


logger = logging.getLogger(__name__)

SNAKE_CASE_WARNING = "Column name '{field_name}' appears to be snake_case. camelCase is expected."


def _warn_if_snake_case(field_name: str) -> None:
    """Warn if a field name uses snake_case instead of camelCase."""
    if "_" in field_name:
        logger.warning(SNAKE_CASE_WARNING.format(field_name=field_name))


class PlatformOutputRecordSets:
    """Class to  in the Open Targets Platform data."""

    record_sets: list[mlc.RecordSet]
    DISTRIBUTION_ID: str
    spark: SparkSession

    def __init__(self: PlatformOutputRecordSets) -> None:
        self.record_sets = []
        self.spark = SparkSession.builder.getOrCreate()
        super().__init__()  # <- What is the parent class here?

    def get_metadata(self: PlatformOutputRecordSets) -> list[mlc.RecordSet]:
        """Return the distribution metadata."""
        return self.record_sets

    def add_assets_from_paths(self: PlatformOutputRecordSets, paths: list[str]):
        """Add files from a list to the distribution."""
        for path in paths:
            self.DISTRIBUTION_ID = path.split("/")[-1]
            record_set = self.get_fileset_recordset(path)

            # Append the recordset to the record sets list:
            self.record_sets.append(record_set)

        return self
    
    def generate_distribution_description(self: PlatformOutputRecordSets, id: str) -> str:
        """Generate the description of the distribution."""
        description = DistributionCuration().get_curation(id, "description")

        # Return basic description if curation is not available:
        if description is None:
            return f"Description of the distribution '{id}' is not available."

        # Extract tags:
        tags = DistributionCuration().get_curation(
            distribution_id=id, key="tags", log_level=logging.DEBUG
        )

        # Return description if tags are not available:
        if not isinstance(tags, list):
            return description

        # Format tags:
        return f"{description} [{', '.join(tags)}]"

    def get_fileset_recordset(
        self: PlatformOutputRecordSets, path: str, 
    ) -> mlc.RecordSet:
        """Returns the recordset for a fileset."""
        # Get the schema from the recordset:
        try:
            schema = self.spark.read.parquet(path).schema
        except AnalysisException:
            logger.error(f'Could not read parquet: {path}')
            raise ValueError(f'Could not read dataset: {path}')

        record_set = mlc.RecordSet(
            id=self.DISTRIBUTION_ID,
            name=self.DISTRIBUTION_ID,
            fields=[self.parse_spark_field(field) for field in schema],
        )
        # Add primary key to recordset, if available:
        primary_key = DistributionCuration().get_curation(
            distribution_id=self.DISTRIBUTION_ID, key="key"
        )
        if primary_key:
            record_set.key = primary_key

        # Extract description of dataset:
        record_set.description = self.generate_distribution_description(self.DISTRIBUTION_ID)

        # Return record set
        return record_set

    def parse_spark_field(
        self: PlatformOutputRecordSets, field: t.StructField, parent: str | None = None
    ) -> mlc.Field:
        
        def get_field_description(field: t.StructField, field_id: str) -> str:
            """Get the field description."""
            # Get the description from the data:
            description = get_field_description_from_data(field)
            if description:
                return description
            
            # If no description is found in the data, get it from the curation:
            description = get_field_description_from_curation(field_id)
            if description:
                return description
            
            # No description found, return a placeholder:
            return f"PLACEHOLDER for {field.name} description"
            
        def get_field_description_from_curation(field_id: str) -> str | None:
            """Get the field description from the curation."""
            return RecordsetCuration().get_curation(
                distribution_id=field_id, key="description"
            )

        def get_field_description_from_data(field: t.StructField) -> str | None:
            metadata: dict[str, str] | None = field.metadata

            if metadata and "description" in metadata:
                return metadata["description"]
            else:
                return None

        def get_field_id(
            parent: str | None,
            field: t.StructField,
            include_distribution_id: bool = True,
        ) -> str:
            """Get the field id."""
            column_id: str
            if parent:
                column_id = f"{parent}/{field.name}"
            else:
                column_id = field.name
            if include_distribution_id:
                column_id = f"{self.DISTRIBUTION_ID}/{column_id}"
            return column_id

        def get_foreign_key(field: t.StructField, field_id: str) -> str | None:
            """Get the foreign key from the curation."""
            metadata: dict[str, str] | None = field.metadata

            # If the data contains a foreign key, use it:
            if metadata and "foreign_key" in metadata:
                return metadata["foreign_key"]
            
            # If the data does not contain a foreign key, get it from the curation:
            return RecordsetCuration().get_curation(
                distribution_id=field_id, key="foreign_key", log_level=logging.DEBUG
            )

        _warn_if_snake_case(field.name)

        field_type: str = field.dataType.typeName() # <- This might be a map. Not yet supported by croissant.

        # Get the field description from the data:
        column_description: str = get_field_description(field, get_field_id(parent, field))

        # Get foreign key from the data:
        
        # Initialise field:
        croissant_field = mlc.Field(
            id=get_field_id(parent, field),
            name=field.name,
            description=column_description,
            source=mlc.Source(
                file_set=self.DISTRIBUTION_ID + "-fileset",
                extract=mlc.Extract(column=get_field_id(parent, field, False)),
            ),  
        )

        if foreign_key := get_foreign_key(field, get_field_id(parent, field)):
            croissant_field.references = mlc.Source(field=foreign_key)

        if field_type in typeDict.keys():
            croissant_field.data_types.append(typeDict.get(field_type))

        # Test if the field is a list:
        if field_type == "array":
            element_type = field.dataType.elementType
            croissant_field.repeated = True
            
            # A list of struct:
            if element_type.typeName() == "struct":
                croissant_field.sub_fields = [
                    self.parse_spark_field(subfield, get_field_id(parent, field, False))
                    for subfield in element_type
                ]
            
            # If element type is a primitive type:
            elif element_type.typeName() in typeDict.keys():
                # Append data type of the primitive type
                croissant_field.data_types.append(typeDict.get(element_type.typeName()))
            
            # If the element type is an other array, we flatten it
            if element_type.typeName() == "array":
                logger.warning(f"Field {field.name} is of type array of array. This is not yet supported by croissant. Flattening.")
                sub_element_type = element_type.elementType
                croissant_field.data_types.append(typeDict.get(sub_element_type.typeName()))

        # Test if the field is a struct:
        elif field_type == "struct":
            croissant_field.sub_fields = [
                self.parse_spark_field(subfield, get_field_id(parent, field, False))
                for subfield in field.dataType
            ]
        elif field_type == 'map':
            logger.warning(f"Field {self.DISTRIBUTION_ID}/{field.name} is of type map. This is not yet supported by croissant.")
            
            # Extracting keys/values:
            key_type = field.dataType.keyType
            value_type = field.dataType.valueType

            # Constructing an artifical struct:
            struct = t.StructType([
                t.StructField('key', key_type),
                t.StructField('value', value_type)
            ])

            # Modelling maps as arrays:
            croissant_field.repeated = True

            # Adding key/value fields:
            croissant_field.sub_fields = [
                self.parse_spark_field(subfield, get_field_id(parent, field, False))
                for subfield in struct
            ]
            
        return croissant_field
