"""Class to create the croissant distribution metadata for the Open Targets Platform."""

import logging
from mlcroissant import FileSet, FileObject
from ot_croissant.curation import DistributionCuration

logger = logging.getLogger(__name__)


class PlatformOutputDistribution:
    """Class to store the list of FileSets or FileObjects in the Open Targets Platform data."""

    distribution: list[FileSet | FileObject]
    contained_in: list[str]

    def __init__(self):
        self.distribution = []
        self.contained_in = []
        self.curation = DistributionCuration()
        super().__init__()

    def get_metadata(self):
        """Return the distribution metadata."""
        return self.distribution

    def generate_distribution_description(self, id: str) -> str:
        """Generate the description of the distribution."""
        description = self.curation.get_curation(id, "description")

        # Return basic description if curation is not available:
        if description is None:
            return f"Description of the distribution '{id}' is not available."

        # Extract tags:
        tags = self.curation.get_curation(
            distribution_id=id, key="tags", log_level=logging.DEBUG
        )

        # Return description if tags are not available:
        if not isinstance(tags, list):
            return description

        # Format tags:
        return f"{description} [{', '.join(tags)}]"

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
                    encoding_formats="https",
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
                encoding_formats="https",
                content_url=gcp_location,
                sha256=data_integrity_hash,
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
                name=(
                    self.curation.get_curation(id, "nice_name")
                    if self.curation.get_curation(id, "nice_name")
                    else f"Automatic nice_name of the file set/object '{id}'."
                ),
                description=self.generate_distribution_description(id),
                encoding_formats="application/x-parquet",
            )

            if len(self.contained_in) > 0:
                fileset.contained_in = self.contained_in

            self.distribution.append(fileset)
        return self
