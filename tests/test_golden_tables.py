"""Golden-file (SHA-256) verification for versioned metric tables in outputs/tables/."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = REPO_ROOT / "outputs" / "tables"
GOLDEN_HASHES_PATH = REPO_ROOT / "tests" / "fixtures" / "golden_table_hashes.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def golden_table_hashes() -> dict[str, str]:
    return json.loads(GOLDEN_HASHES_PATH.read_text(encoding="utf-8"))


def test_golden_table_hashes_match_versioned_csvs(golden_table_hashes: dict[str, str]) -> None:
    missing_files = [name for name in golden_table_hashes if not (TABLES_DIR / name).exists()]
    assert not missing_files, f"missing versioned tables: {missing_files}"

    mismatches: list[str] = []
    for filename, expected_hash in sorted(golden_table_hashes.items()):
        actual_hash = _sha256_file(TABLES_DIR / filename)
        if actual_hash != expected_hash:
            mismatches.append(f"{filename}: expected {expected_hash}, got {actual_hash}")

    assert not mismatches, "golden table hash mismatches:\n" + "\n".join(mismatches)


def test_golden_manifest_covers_all_top_level_csv_tables(golden_table_hashes: dict[str, str]) -> None:
    """Every official CSV directly under outputs/tables/ must have a golden hash."""
    official_csvs = sorted(path.name for path in TABLES_DIR.glob("*.csv"))
    assert official_csvs, "expected versioned CSV tables under outputs/tables/"

    uncovered = [name for name in official_csvs if name not in golden_table_hashes]
    assert not uncovered, (
        "add SHA-256 entries for new official tables in tests/fixtures/golden_table_hashes.json: "
        + ", ".join(uncovered)
    )
