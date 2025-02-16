"""Classes for overall OT Platform metadata."""

from mlcroissant import Metadata
from ot_croissant.crumbs.distribution import PlatformOutputDistribution
from ot_croissant.crumbs.record_sets import PlatformOutputRecordSets


class PlatformOutputMetadata(Metadata):
    """Class extending the Metadata class from MLCroissant to define the OT Platform metadata."""

    NAME = "Open Targets Platform"
    DESCRIPTION = "The Open Targets Platform contains data to assist the target identification and prioritisation of drug targets."
    CITE_AS = "Open Targets"
    URL = "https://platform.opentargets.org"

    FILESET = [
        "/Users/dsuveges/project_data/gentropy/disease",
    ]

    def __init__(self):
        super().__init__(
            name=self.NAME,
            description=self.DESCRIPTION,
            cite_as=self.CITE_AS,
            url=self.URL,
            license=self.LICENCE,
            distribution=(
                PlatformOutputDistribution()
                .add_assets_from_paths(paths=datasets)
                .get_metadata()
            ),
            record_sets=PlatformOutputRecordSets()
            .add_assets_from_paths(paths=datasets)
            .get_metadata(),
        )
