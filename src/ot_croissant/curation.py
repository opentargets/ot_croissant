"""Manual curation of OT-Croissant datasets."""
from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class BaseCuration(ABC):
    """Abstract base class for curation logic."""

    curation: dict = field(default_factory=dict)

    @property
    @abstractmethod
    def curation_path(self: BaseCuration) -> Path:
        """Path to the curation JSON file.
        
        Returns:
            Path to the curation JSON file.
        """
        pass

    @abstractmethod
    def get_warning_message(self: BaseCuration, distribution_id: str, key: str) -> str:
        """Generate a warning message for missing curation.
        
        Args:
            distribution_id: The ID of the distribution.
            key: The key of the curation.
            
        Returns:
            Warning message string.
        """
        pass

    def __post_init__(self: BaseCuration) -> None:
        """Load curation data from the specified JSON file."""
        
        with open(self.curation_path, "r") as f:
            data_list = json.load(f)
        
        self.curation = {item["id"]: item for item in data_list}

    def get_curation(self: BaseCuration, distribution_id: str, key: str) -> str | None:
        """Get curation entry for a given distribution ID and key.

        Args:
            distribution_id: The ID of the distribution.
            key: The key of the curation.

        Returns:
            The value of the curation or None if not found.
        """
        curation_entry = self.curation.get(distribution_id)
        if curation_entry and key in curation_entry:
            return curation_entry[key]
        else:
            logger.warning(self.get_warning_message(distribution_id, key))
            return None


class DistributionCuration(BaseCuration):
    """Curation logic for distribution datasets."""

    @property
    def curation_path(self: DistributionCuration) -> Path:
        """Path to the curation JSON file for distribution datasets.
        Returns:
            Path to the curation JSON file.
        """
        return Path(__file__).parent / "assets/distribution.json"

    def get_warning_message(self: DistributionCuration, distribution_id: str, key: str) -> str:
        """Generate a warning message for missing curation in distribution datasets.
        Args:
            distribution_id: The ID of the distribution.
            key: The key of the curation.
        Returns:
            Warning message string.
        """
        return f"[Distribution]: Key '{key}' not found in curation table for '{distribution_id}'."


class RecordsetCuration(BaseCuration):
    """Curation logic for recordset datasets."""

    @property
    def curation_path(self) -> Path:
        return Path(__file__).parent / "assets/recordset.json"

    def get_warning_message(self, distribution_id: str, key: str) -> str:
        return f"[Recordset]: Field '{key}' not found in curation table for '{distribution_id}'."