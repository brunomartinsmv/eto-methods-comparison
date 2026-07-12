"""Tests for Zenodo release publishing helpers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts import publish_zenodo_release as zenodo


def test_build_metadata_v200_uses_zenodo_json_and_changelog() -> None:
    metadata = zenodo._build_metadata("v2.0.0")["metadata"]

    assert metadata["version"] == "v2.0.0"
    assert metadata["publication_date"] == "2026-07-12"
    assert "Reproducible Python pipeline" in metadata["description"]
    assert "CHANGELOG.md#200---2026-07-12" in metadata["description"]
    assert metadata["related_identifiers"][0]["identifier"].endswith("/tree/v2.0.0")
    assert metadata["license"] == "mit"


def test_changelog_entry_for_tag_unknown_version_raises(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [Unreleased]\n\n## [2.0.0] - 2026-07-12\n", encoding="utf-8")

    with pytest.raises(zenodo.ZenodoError, match="No CHANGELOG entry found"):
        zenodo._changelog_entry_for_tag("v9.9.9", changelog)


def test_github_heading_anchor_matches_github_slug() -> None:
    assert zenodo._github_heading_anchor("[2.0.0] - 2026-07-12") == "200---2026-07-12"


def test_download_http_error_raises_zenodo_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import urllib.error

    def fake_urlopen(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://example.com/archive.zip",
            404,
            "Not Found",
            hdrs=None,
            fp=MagicMock(read=lambda: b"release not found"),
        )

    monkeypatch.setattr(zenodo.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(zenodo.ZenodoError, match="GET .* failed \\(404\\)"):
        zenodo._download("https://example.com/archive.zip", tmp_path / "archive.zip")


def test_publish_release_dry_run_skips_publish(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []

    def fake_request(method: str, url: str, **_kwargs) -> dict:
        calls.append((method, url))
        if method == "POST" and url.endswith("/actions/newversion"):
            return {"links": {"latest_draft": "https://zenodo.org/api/deposit/depositions/99"}}
        if method == "GET":
            return {
                "id": 99,
                "links": {"bucket": "https://zenodo.org/api/files/bucket/abc"},
                "files": [{"links": {"self": "https://zenodo.org/api/files/1"}}],
            }
        if method == "DELETE":
            return {}
        if method == "PUT" and "/depositions/" in url:
            return {
                "id": 99,
                "state": "draft",
                "links": {
                    "self": "https://zenodo.org/api/deposit/depositions/99",
                    "record_html": "https://zenodo.org/deposit/99",
                },
            }
        if method == "PUT":
            return {}
        raise AssertionError(f"Unexpected request: {method} {url}")

    def fake_download(url: str, destination: Path, **_kwargs) -> None:
        destination.write_bytes(b"archive")

    monkeypatch.setattr(zenodo, "_request", fake_request)
    monkeypatch.setattr(zenodo, "_download", fake_download)

    zenodo_json = tmp_path / ".zenodo.json"
    changelog = tmp_path / "CHANGELOG.md"
    zenodo_json.write_text(
        json.dumps({"description": "Test description", "license": "mit"}),
        encoding="utf-8",
    )
    changelog.write_text("## [1.0.0] - 2026-02-11\n", encoding="utf-8")

    result = zenodo.publish_release(
        tag="v1.0.0",
        deposition_id="18615164",
        token="token",
        dry_run=True,
        zenodo_path=zenodo_json,
        changelog_path=changelog,
    )

    assert result["state"] == "draft"
    assert not any(method == "POST" and url.endswith("/actions/publish") for method, url in calls)


def test_main_missing_token_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert zenodo.main(["--tag", "v2.0.0", "--token", ""]) == 1
    assert "Missing Zenodo token" in capsys.readouterr().err
