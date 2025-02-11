"""Class to create the croissant distribution metadata for the Open Targets Platform."""

from mlcroissant import FileSet, FileObject
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
    def get_curations():
        """Returns dictionary of file set/objects curations (incl. nice_name and description)."""
        import json

        with open("src/ot_croissant/curation/distribution.json", "r") as f:
            data_list = json.load(f)

        data_dict = {item["id"]: item for item in data_list}
        return data_dict

    @staticmethod
    def get_distribution_curation(id: str, key: str) -> str:
        """Returns the curation value of the distribution."""
        value = f"Automatic {key} of the file set/object '{id}'."
        curations = PlatformOutputDistribution.get_curations()
        curation_entry = curations.get(id)
        if curation_entry and key in curation_entry:
            value = curation_entry[key]
        else:
            logging.warning(
                f"[Distribution]: ID '{id}' not found in curation/distribution or has no {key}."
            )
        return value

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
