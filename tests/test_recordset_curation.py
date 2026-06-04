"""Tests for the per-dataset recordset curation files and Pydantic models."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ot_croissant.models import (
    DistributionAnnotation,
    InstanceAnnotation,
    RecordsetFieldAnnotation,
)

ASSETS_DIR = Path(__file__).parent.parent / 'src/ot_croissant/assets'
RECORDSET_DIR = ASSETS_DIR / 'recordset'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_all_recordset_entries() -> dict[str, dict]:
    """Load every per-dataset curation file and return a merged {dataset/field: entry} map."""
    corpus: dict[str, dict] = {}
    for path in sorted(RECORDSET_DIR.glob('*.json')):
        dataset = path.stem
        for entry in json.loads(path.read_text()):
            corpus[f'{dataset}/{entry["id"]}'] = entry
    return corpus


@pytest.fixture(scope='module')
def recordset_corpus() -> dict[str, dict]:
    return _load_all_recordset_entries()


# ---------------------------------------------------------------------------
# Recordset file integrity
# ---------------------------------------------------------------------------


def test_recordset_files_are_valid_json():
    for path in RECORDSET_DIR.glob('*.json'):
        try:
            json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            pytest.fail(f'{path.name} is not valid JSON: {exc}')


def test_recordset_entries_conform_to_model():
    """Every entry in every recordset file must validate as RecordsetFieldAnnotation."""
    errors = []
    for path in sorted(RECORDSET_DIR.glob('*.json')):
        for entry in json.loads(path.read_text()):
            try:
                RecordsetFieldAnnotation.model_validate(entry)
            except ValidationError as exc:
                errors.append(f'{path.name}/{entry.get("id", "?")}: {exc}')
    assert not errors, 'Recordset entries failed model validation:\n' + '\n'.join(errors)


def test_recordset_ids_are_unique_within_file():
    """Each per-dataset file must not contain duplicate field ids."""
    violations = []
    for path in sorted(RECORDSET_DIR.glob('*.json')):
        ids = [e['id'] for e in json.loads(path.read_text())]
        dups = sorted({x for x in ids if ids.count(x) > 1})
        if dups:
            violations.append(f'{path.name}: {dups}')
    assert not violations, 'Files with duplicate field ids:\n' + '\n'.join(violations)


def test_no_entry_id_contains_dataset_prefix():
    """Ensure the dataset prefix was stripped — ids should never start with '<dataset>/'."""
    violations = [
        f'{path.name}: {entry["id"]}'
        for path in RECORDSET_DIR.glob('*.json')
        for entry in json.loads(path.read_text())
        if entry['id'].startswith(f'{path.stem}/')
    ]
    assert not violations, f'Entries with un-stripped dataset prefix: {violations}'


def test_foreign_keys_reference_existing_fields(recordset_corpus):
    """Every foreign_key value must point to a dataset/field that exists in the corpus."""
    bad = []
    for full_id, entry in recordset_corpus.items():
        fk = entry.get('foreign_key')
        if fk and fk not in recordset_corpus:
            bad.append(f'{full_id} → {fk}')
    assert not bad, 'Foreign keys pointing to non-existent fields:\n' + '\n'.join(bad)


# ---------------------------------------------------------------------------
# Distribution asset
# ---------------------------------------------------------------------------


def test_distribution_file_conforms_to_model():
    """Every entry in distribution.json must validate as DistributionAnnotation."""
    errors = []
    for entry in json.loads((ASSETS_DIR / 'distribution.json').read_text()):
        try:
            DistributionAnnotation.model_validate(entry)
        except ValidationError as exc:
            errors.append(f'{entry.get("id", "?")}: {exc}')
    assert not errors, 'Distribution entries failed model validation:\n' + '\n'.join(errors)


def test_distribution_ids_are_unique():
    entries = json.loads((ASSETS_DIR / 'distribution.json').read_text())
    ids = [e['id'] for e in entries]
    duplicates = [id_ for id_ in set(ids) if ids.count(id_) > 1]
    assert not duplicates, f'Duplicate distribution ids: {duplicates}'


# ---------------------------------------------------------------------------
# Instance asset
# ---------------------------------------------------------------------------


def test_instance_file_conforms_to_model():
    """Every entry in instance.json must validate as InstanceAnnotation."""
    errors = []
    for entry in json.loads((ASSETS_DIR / 'instance.json').read_text()):
        try:
            InstanceAnnotation.model_validate(entry)
        except ValidationError as exc:
            errors.append(f'{entry.get("id", "?")}: {exc}')
    assert not errors, 'Instance entries failed model validation:\n' + '\n'.join(errors)
