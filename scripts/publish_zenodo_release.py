"""Publish a GitHub release tag as a new Zenodo version.

Requires a Zenodo personal access token with deposit:write and deposit:actions
scopes. Set ZENODO_ACCESS_TOKEN in the environment or pass --token.

Example:
    ZENODO_ACCESS_TOKEN=... python -m scripts.publish_zenodo_release \
        --tag v2.0.0 --deposition-id 18615164
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ZENODO_API = "https://zenodo.org/api"
GITHUB_REPO = "brunomartinsmv/eto-methods-comparison"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANGELOG = REPO_ROOT / "CHANGELOG.md"


class ZenodoError(RuntimeError):
    pass


def _request(
    method: str,
    url: str,
    *,
    token: str,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    request_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ZenodoError(f"{method} {url} failed ({exc.code}): {detail}") from exc


def _download(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        handle.write(response.read())


def _delete_inherited_files(deposition: dict, token: str) -> None:
    for file_info in deposition.get("files", []):
        _request("DELETE", file_info["links"]["self"], token=token)


def _changelog_section_anchor(tag: str, changelog_path: Path = DEFAULT_CHANGELOG) -> str:
    version = tag.lstrip("v")
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})",
        re.MULTILINE,
    )
    text = changelog_path.read_text(encoding="utf-8")
    match = pattern.search(text)
    if not match:
        raise ZenodoError(f"No CHANGELOG section found for version {version}")
    return f"{version.replace('.', '')}---{match.group(1)}"


def _build_metadata(tag: str, changelog_path: Path = DEFAULT_CHANGELOG) -> dict:
    changelog_url = (
        f"https://github.com/{GITHUB_REPO}/blob/{tag}/CHANGELOG.md"
        f"#{_changelog_section_anchor(tag, changelog_path)}"
    )
    return {
        "metadata": {
            "title": f"{GITHUB_REPO}: {tag}",
            "upload_type": "software",
            "description": (
                "<p>Major release with full ET0 computation pipeline, UX commands, "
                "uncertainty and sensitivity diagnostics, safety-net CI, and LaTeX "
                f"equation documentation. <strong>Full changelog:</strong> "
                f'<a href="{changelog_url}">{changelog_url}</a></p>'
            ),
            "publication_date": "2026-07-12",
            "version": tag,
            "access_right": "open",
            "license": "mit",
            "creators": [
                {
                    "name": "Vieira, Bruno Martins M.",
                    "affiliation": "Universidade Federal do Mato Grosso",
                }
            ],
            "keywords": [
                "evapotranspiration",
                "reference evapotranspiration",
                "Penman-Monteith",
                "FAO-56",
                "reproducible research",
                "scientific computing",
            ],
            "related_identifiers": [
                {
                    "relation": "isSupplementTo",
                    "identifier": f"https://github.com/{GITHUB_REPO}/tree/{tag}",
                    "resource_type": "software",
                    "scheme": "url",
                }
            ],
        }
    }


def publish_release(
    *,
    tag: str,
    deposition_id: str,
    token: str,
    changelog_path: Path = DEFAULT_CHANGELOG,
) -> dict:
    new_version = _request(
        "POST",
        f"{ZENODO_API}/deposit/depositions/{deposition_id}/actions/newversion",
        token=token,
    )
    draft_url = new_version["links"]["latest_draft"]
    draft = _request("GET", draft_url, token=token)
    draft_id = str(draft["id"])
    bucket_url = draft["links"]["bucket"]

    _delete_inherited_files(draft, token)

    archive_name = f"{GITHUB_REPO.replace('/', '-')}-{tag}.zip"
    archive_url = f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag}.zip"
    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / archive_name
        _download(archive_url, archive_path)
        with archive_path.open("rb") as handle:
            _request(
                "PUT",
                f"{bucket_url}/{urllib.parse.quote(archive_name)}",
                token=token,
                data=handle.read(),
                headers={"Content-Type": "application/octet-stream"},
            )

    _request(
        "PUT",
        f"{ZENODO_API}/deposit/depositions/{draft_id}",
        token=token,
        data=json.dumps(_build_metadata(tag, changelog_path)).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    published = _request(
        "POST",
        f"{ZENODO_API}/deposit/depositions/{draft_id}/actions/publish",
        token=token,
    )
    return published


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Git tag to publish, e.g. v2.0.0")
    parser.add_argument(
        "--deposition-id",
        default="18615164",
        help="Zenodo deposition ID of the latest published version",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("ZENODO_ACCESS_TOKEN", ""),
        help="Zenodo personal access token (or set ZENODO_ACCESS_TOKEN)",
    )
    args = parser.parse_args(argv)

    if not args.token:
        print("Missing Zenodo token. Set ZENODO_ACCESS_TOKEN or pass --token.", file=sys.stderr)
        return 1

    published = publish_release(tag=args.tag, deposition_id=args.deposition_id, token=args.token)
    doi = published.get("doi", "")
    record_id = published.get("id", "")
    print(
        json.dumps(
            {
                "doi": doi,
                "record_id": record_id,
                "record_url": published.get("links", {}).get("record_html"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
