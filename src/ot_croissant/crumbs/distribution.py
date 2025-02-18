"""Class to create the croissant distribution metadata for the Open Targets Platform."""

from mlcroissant import FileSet, FileObject
from ot_croissant.curation import DistributionCuration
import logging


class PlatformOutputDistribution:
    """Class to store the list of FileSets or FileObjects in the Open Targets Platform data."""

    distribution: list[FileSet | FileObject]
    contained_in: list[str]

    def __init__(self):
        self.distribution = []
        self.contained_in = []
        super().__init__()

    def get_metadata(self):
        """Return the distribution metadata."""
        return self.distribution

    @staticmethod
    def get_distribution_curation(id: str, key: str) -> str:
        """Returns the curation value of the distribution."""
        curation_entry = DistributionCuration().get_curation(
            distribution_id=id, key=key
        )
        if curation_entry:
            return curation_entry
        else:
            return f"Automatic {key} of the file set/object '{id}'."

    def add_ftp_location(self, ftp_location: str):
        """Add the FTP location of the distribution."""
        self.distribution.append(
            FileObject(
                id="ftp-location",
                name="FTP location",
                description="FTP location of the Open Targets Platform data.",
                encoding_format="https",
                content_url=ftp_location,
                sha256="https://github.com/mlcommons/croissant/issues/80",
            )
        )
        self.contained_in.append("ftp-location")
        return self

    def add_gcp_location(self, gcp_location: str):
        """Add the GCP location of the distribution."""
        self.distribution.append(
            FileObject(
                id="gcp-location",
                name="GCP location",
                description="Location of the Open Targets Platform data in Google Cloud Storage.",
                encoding_format="https",
                content_url=gcp_location,
                sha256="https://github.com/mlcommons/croissant/issues/80",
            )
        )
        self.contained_in.append("gcp-location")
        return self

    def add_assets_from_paths(self, paths: list[str]):
        """Add files from a list to the distribution."""
        ids = [path.split("/")[-1] for path in paths]
        for id in ids:
            fileset = FileSet(
                id=id + "-fileset",
                name=self.get_distribution_curation(id, "nice_name"),
                description=self.get_distribution_curation(id, "description"),
                encoding_format="application/x-parquet",
                includes=f"{id}/*.parquet",
            )

            if len(self.contained_in) > 0:
                fileset.contained_in = self.contained_in

            self.distribution.append(fileset)
        return self
