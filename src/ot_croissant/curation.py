"""Manual curation of OT-Croissant datasets."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from loguru import logger
from pydantic import BaseModel

from ot_croissant.models import DistributionAnnotation, InstanceAnnotation, RecordsetFieldAnnotation

T = TypeVar('T', bound=BaseModel)


class BaseCuration(ABC, Generic[T]):
    """Abstract base class for single-file curation tables.

    Subclasses declare which file to load (``curation_path``) and which Pydantic
    model to validate entries against (``_model``). Entries are keyed by their
    ``id`` field.
    """

    def __init__(self) -> None:
        data = json.loads(self.curation_path.read_text())
        self._curation: dict[str, T] = {item['id']: self._model.model_validate(item) for item in data}

    @property
    @abstractmethod
    def curation_path(self) -> Path:
        """Path to the JSON curation file."""

    @property
    @abstractmethod
    def _model(self) -> type[T]:
        """Pydantic model class used to validate each entry."""

    def get(self, id: str, log_level: str = 'WARNING') -> T | None:
        """Return the curation entry for *id*, or ``None`` if not found."""
        entry = self._curation.get(id)
        if entry is None:
            logger.log(
                log_level,
                f"[{type(self).__name__}]: No curation entry found for '{id}'.",
            )
        return entry


class DistributionCuration(BaseCuration[DistributionAnnotation]):
    """Curation for top-level dataset distributions."""

    @property
    def curation_path(self) -> Path:
        """Path to the distribution curation file."""
        return Path(__file__).parent / 'assets/distribution.json'

    @property
    def _model(self) -> type[DistributionAnnotation]:
        """Pydantic model for distribution entries."""
        return DistributionAnnotation


class InstanceCuration(BaseCuration[InstanceAnnotation]):
    """Curation for Platform instances (public / ppp)."""

    @property
    def curation_path(self) -> Path:
        """Path to the instance curation file."""
        return Path(__file__).parent / 'assets/instance.json'

    @property
    def _model(self) -> type[InstanceAnnotation]:
        """Pydantic model for instance entries."""
        return InstanceAnnotation


class RecordsetCuration:
    """Curation for individual fields within recordset datasets.

    Loads per-dataset JSON files from ``assets/recordset/<dataset>.json`` lazily
    and caches them at the class level so each file is read at most once per
    process.
    """

    _RECORDSET_DIR = Path(__file__).parent / 'assets/recordset'
    _cache: dict[str, dict[str, RecordsetFieldAnnotation]] = {}

    def _load_dataset(self, dataset: str) -> dict[str, RecordsetFieldAnnotation]:
        if dataset not in self._cache:
            path = self._RECORDSET_DIR / f'{dataset}.json'
            if not path.exists():
                self._cache[dataset] = {}
                return {}
            entries = json.loads(path.read_text())
            self._cache[dataset] = {e['id']: RecordsetFieldAnnotation.model_validate(e) for e in entries}
        return self._cache[dataset]

    def get_field(self, distribution_id: str, log_level: str = 'WARNING') -> RecordsetFieldAnnotation | None:
        """Return the annotation for a field, or ``None`` if not found.

        Args:
            distribution_id: Full field path as ``dataset/field`` or
                ``dataset/parent/field`` for nested fields.
            log_level: Loguru level used when the entry is missing.
        """
        if '/' not in distribution_id:
            logger.log(
                log_level,
                f"[RecordsetCuration]: Unexpected id format '{distribution_id}' — expected 'dataset/field'.",
            )
            return None

        dataset, field_path = distribution_id.split('/', 1)
        entry = self._load_dataset(dataset).get(field_path)
        if entry is None:
            logger.log(
                log_level,
                f"[RecordsetCuration]: No curation entry found for '{distribution_id}'.",
            )
        return entry
