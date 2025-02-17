"""Manual curation of OT-Croissant datasets."""

import logging


class DistributionCuration:
    """Class containing the manual curation of FileSets or FileObjects in the Open Targets Platform data."""

    curation: dict

    def __init__(self):
        """Read curation from curation json file."""
        import json
        from pathlib import Path

        curation_path = Path(__file__).parent / "assets/distribution.json"
        with open(curation_path, "r") as f:
            data_list = json.load(f)

        self.curation = {item["id"]: item for item in data_list}

    def get_curation(self, distribution_id: str, key: str) -> str | None:
        """Get distribution curation.

        Args:
            distribution_id: The id of the distribution.
            key: The key of the curation.

        Returns:
            The value of the curation or None if not found.
        """
        curation_entry = self.curation.get(distribution_id)
        if curation_entry and key in curation_entry:
            return curation_entry[key]
        else:
            logging.warning(
                f"[Distribution]: Key '{key}' not found in curation table for'{distribution_id}'."
            )
            return None
