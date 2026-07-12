import io
import json
from pathlib import Path
from unittest import mock
import urllib.error

import pytest

from scripts import publish_zenodo_release as zenodo


def test_changelog_section_anchor_reads_version_date() -> None:
    changelog = Path("CHANGELOG.md")

    anchor = zenodo._changelog_section_anchor("v2.0.0", changelog)

    assert anchor == "200---2026-07-12"


def test_changelog_section_anchor_rejects_unknown_version(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("## [1.0.0] - 2026-01-01\n", encoding="utf-8")

    with pytest.raises(zenodo.ZenodoError, match="No CHANGELOG section found"):
        zenodo._changelog_section_anchor("v9.9.9", changelog)


def test_build_metadata_links_to_changelog_section() -> None:
    metadata = zenodo._build_metadata("v2.0.0")

    description = metadata["metadata"]["description"]
    assert "200---2026-07-12" in description
    assert metadata["metadata"]["version"] == "v2.0.0"


def test_main_requires_token(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = zenodo.main(["--tag", "v2.0.0", "--token", ""])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Missing Zenodo token" in captured.err


@mock.patch("scripts.publish_zenodo_release._download")
@mock.patch("scripts.publish_zenodo_release._request")
def test_publish_release_runs_zenodo_flow(
    mock_request: mock.Mock,
    mock_download: mock.Mock,
) -> None:
    def _fake_download(_url: str, destination: Path) -> None:
        destination.write_bytes(b"zip")

    mock_download.side_effect = _fake_download
    mock_request.side_effect = [
        {"links": {"latest_draft": "https://zenodo.org/api/deposit/depositions/999"}},
        {
            "id": 999,
            "links": {"bucket": "https://zenodo.org/api/files/bucket-1"},
            "files": [{"links": {"self": "https://zenodo.org/api/files/old.zip"}}],
        },
        {},
        {},
        {},
        {"doi": "10.5281/zenodo.999", "id": 999, "links": {"record_html": "https://zenodo.org/record/999"}},
    ]

    published = zenodo.publish_release(
        tag="v2.0.0",
        deposition_id="18615164",
        token="test-token",
    )

    assert published["doi"] == "10.5281/zenodo.999"
    assert mock_request.call_count == 6
    mock_download.assert_called_once()

    delete_call = mock_request.call_args_list[2]
    assert delete_call.args[0] == "DELETE"
    assert delete_call.kwargs["token"] == "test-token"

    upload_call = mock_request.call_args_list[3]
    assert upload_call.args[0] == "PUT"
    assert "bucket-1" in upload_call.args[1]

    metadata_call = mock_request.call_args_list[4]
    payload = json.loads(metadata_call.kwargs["data"].decode("utf-8"))
    assert payload["metadata"]["version"] == "v2.0.0"

    publish_call = mock_request.call_args_list[5]
    assert publish_call.args[0] == "POST"
    assert publish_call.args[1].endswith("/actions/publish")


@mock.patch("scripts.publish_zenodo_release.urllib.request.urlopen")
def test_request_raises_zenodo_error_on_http_failure(mock_urlopen: mock.Mock) -> None:
    error = urllib.error.HTTPError(
        "https://zenodo.org/api/deposit/depositions/1/actions/newversion",
        403,
        "Forbidden",
        hdrs=None,
        fp=io.BytesIO(b'{"message":"forbidden"}'),
    )
    mock_urlopen.side_effect = error

    with pytest.raises(zenodo.ZenodoError, match="403"):
        zenodo._request(
            "POST",
            "https://zenodo.org/api/deposit/depositions/1/actions/newversion",
            token="test-token",
        )
