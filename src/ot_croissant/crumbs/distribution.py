"""Class to create the croissant distribution metadata for the Open Targets Platform."""

from mlcroissant import FileSet, FileObject
from ot_croissant.curation import DistributionCuration
import logging


class PlatformOutputDistribution:
    """Class to store the list of FileSets or FileObjects in the Open Targets Platform data."""

    distribution: list[FileSet | FileObject]

    def __init__(self):
        self.distribution = []
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

    def add_assets_from_paths(self, paths: list[str]):
        """Add files from a list to the distribution."""
        ids = [path.split("/")[-1] for path in paths]
        for id in ids:
            self.distribution.append(
                FileSet(
                    id=id + "-fileset",
                    name=self.get_distribution_curation(id, "nice_name"),
                    description=self.get_distribution_curation(id, "description"),
                    encoding_format="application/vnd.apache.parquet",
                    includes=f"{id}/*.parquet",
                )
            )
        return self
