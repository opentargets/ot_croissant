"""Class to create the croissant distribution metadata for the Open Targets Platform."""

import logging
from mlcroissant import FileSet, FileObject
from ot_croissant.curation import DistributionCuration
from pyspark.sql import SparkSession, types as t
logger = logging.getLogger(__name__)




class PlatformOutputDistribution:
    """Class to store the list of FileSets or FileObjects in the Open Targets Platform data."""

    distribution: list[FileSet | FileObject]
    contained_in: list[str]

    def __init__(self):
        self.distribution = []
        self.contained_in = []
        self.curation = DistributionCuration()
        
        self.spark = SparkSession.builder.getOrCreate()
        self.spark_context = self.spark.sparkContext

        super().__init__()

    def get_metadata(self):
        """Return the distribution metadata."""
        return self.distribution

    def add_ftp_location(self, ftp_location: str, data_integrity_hash: str):
        """Add the FTP location of the distribution IF ftp location is not None.

        Args:
            ftp_location: The FTP location of the distribution.
            data_integrity_hash: The data integrity hash of the distribution.

        Returns:
            The PlatformOutputDistribution object.
        """
        if ftp_location:
            self.distribution.append(
                FileObject(
                    id="ftp-location",
                    name="FTP location",
                    description="FTP location of the Open Targets Platform data.",
                    encoding_formats="application/x-ftp-directory",
                    content_url=ftp_location,
                    sha256=data_integrity_hash,
                )
            )
            self.contained_in.append("ftp-location")

        return self

    def add_gcp_location(self, gcp_location: str, data_integrity_hash: str):
        """Add the GCP location of the distribution."""
        self.distribution.append(
            FileObject(
                id="gcp-location",
                name="GCP location",
                description="Location of the Open Targets Platform data in Google Cloud Storage.",
                encoding_formats="application/x-gcp-directory",
                content_url=gcp_location,
                sha256=data_integrity_hash,
            )
        )
        self.contained_in.append("gcp-location")
        return self

    def add_assets_from_paths(self, paths: list[str]):
        """Add files from a list to the distribution."""
        for path in paths:

            # Extracting dataset name:
            id = path.split("/")[-1]

            # Get columns the dataset is partitioned by:
            partitioned_by = self._partitioned_by(path)
            
            # The includes depends on if the dataset has hyve partition:
            includes = f"{id}/**/*.parquet" if len(partitioned_by) > 0 else f"{id}/*.parquet"

            # Description:
            description = f"Files containing all partitions of the {id} dataset" 
            
            # If the dataset is partitioned by any field, add to description:
            if len(partitioned_by) > 0:
                description += f" partitioned by {','.join(partitioned_by)}"

            # Generating fileset description:
            fileset = FileSet(
                id=id + "-fileset",
                name=(
                    self.curation.get_curation(id, "nice_name")
                    if self.curation.get_curation(id, "nice_name")
                    else f"Automatic nice_name of the file set/object '{id}'."
                ),
                description=description,
                encoding_formats="application/vnd.apache.parquet",
                includes=includes
            )

            if len(self.contained_in) > 0:
                fileset.contained_in = self.contained_in

            self.distribution.append(fileset)
        return self


    def _partitioned_by(self, path: str) -> list[str]:
        """Checking if the dataset has hyve partition via interacting with spark context.
        
        Args:
            path (str): path to the dataset

        Returns:
            list[str]: List of columns the dataset is partitioned by
        """
        # List all files and folders in the path
        fs = self.spark_context._jvm.org.apache.hadoop.fs.FileSystem.get(self.spark_context._jsc.hadoopConfiguration())
        p = self.spark_context._jvm.org.apache.hadoop.fs.Path(path)
        statuses = fs.listStatus(p)

        # Find folders with '=' in their name (Hive partition folders)
        partition_cols = []
        for status in statuses:
            name = status.getPath().getName()
            if status.isDirectory() and '=' in name:
                col = name.split('=')[0]
                partition_cols.append(col)
        
        return list(set(partition_cols))