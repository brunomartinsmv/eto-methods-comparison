"""Publish a GitHub release tag as a new Zenodo version.

Requires a Zenodo personal access token with deposit:write and deposit:actions
scopes. Set ZENODO_ACCESS_TOKEN in the environment or pass --token.

Example:
    ZENODO_ACCESS_TOKEN=... python -m scripts.publish_zenodo_release \
        --tag v2.0.0 --deposition-id 21341983
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
DEFAULT_TIMEOUT = 120
DEFAULT_ZENODO_JSON = Path(".zenodo.json")
DEFAULT_CHANGELOG = Path("CHANGELOG.md")


class ZenodoError(RuntimeError):
    pass


def _github_heading_anchor(heading: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", heading.lower())
    return re.sub(r"\s+", "-", slug.strip())


def _changelog_entry_for_tag(tag: str, changelog_path: Path = DEFAULT_CHANGELOG) -> tuple[str, str]:
    version = tag.removeprefix("v")
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})\s*$",
        re.MULTILINE,
    )
    match = pattern.search(changelog_path.read_text(encoding="utf-8"))
    if match is None:
        raise ZenodoError(
            f"No CHANGELOG entry found for {tag!r} in {changelog_path}. "
            f"Expected a heading like '## [{version}] - YYYY-MM-DD'."
        )
    heading = match.group(0).lstrip("#").strip()
    return match.group(1), _github_heading_anchor(heading)


def _build_metadata(
    tag: str,
    *,
    zenodo_path: Path = DEFAULT_ZENODO_JSON,
    changelog_path: Path = DEFAULT_CHANGELOG,
) -> dict:
    base = json.loads(zenodo_path.read_text(encoding="utf-8"))
    publication_date, anchor = _changelog_entry_for_tag(tag, changelog_path)
    changelog_url = (
        f"https://github.com/{GITHUB_REPO}/blob/{tag}/CHANGELOG.md#{anchor}"
    )
    description = base["description"]
    if not description.startswith("<p>"):
        description = f"<p>{description}</p>"
    base["description"] = (
        f"{description}"
        f'<p><strong>Changelog:</strong> <a href="{changelog_url}">{changelog_url}</a></p>'
    )
    base["publication_date"] = publication_date
    base["version"] = tag
    base["related_identifiers"] = [
        {
            "relation": "isSupplementTo",
            "identifier": f"https://github.com/{GITHUB_REPO}/tree/{tag}",
            "resource_type": "software",
            "scheme": "url",
        }
    ]
    return {"metadata": base}


def _request(
    method: str,
    url: str,
    *,
    token: str,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    request_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ZenodoError(f"{method} {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise ZenodoError(f"{method} {url} failed: {exc.reason}") from exc


def _download(url: str, destination: Path, *, timeout: float = DEFAULT_TIMEOUT) -> None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response, destination.open("wb") as handle:
            handle.write(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ZenodoError(f"GET {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise ZenodoError(f"GET {url} failed: {exc.reason}") from exc


def _delete_inherited_files(deposition: dict, token: str, *, timeout: float) -> None:
    for file_info in deposition.get("files", []):
        _request("DELETE", file_info["links"]["self"], token=token, timeout=timeout)


def publish_release(
    *,
    tag: str,
    deposition_id: str,
    token: str,
    dry_run: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    zenodo_path: Path = DEFAULT_ZENODO_JSON,
    changelog_path: Path = DEFAULT_CHANGELOG,
) -> dict:
    new_version = _request(
        "POST",
        f"{ZENODO_API}/deposit/depositions/{deposition_id}/actions/newversion",
        token=token,
        timeout=timeout,
    )
    draft_url = new_version["links"]["latest_draft"]
    draft = _request("GET", draft_url, token=token, timeout=timeout)
    draft_id = str(draft["id"])
    bucket_url = draft["links"]["bucket"]

    _delete_inherited_files(draft, token, timeout=timeout)

    archive_name = f"{GITHUB_REPO.replace('/', '-')}-{tag}.zip"
    archive_url = f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag}.zip"
    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / archive_name
        _download(archive_url, archive_path, timeout=timeout)
        with archive_path.open("rb") as handle:
            _request(
                "PUT",
                f"{bucket_url}/{urllib.parse.quote(archive_name)}",
                token=token,
                data=handle.read(),
                headers={"Content-Type": "application/octet-stream"},
                timeout=timeout,
            )

    updated = _request(
        "PUT",
        f"{ZENODO_API}/deposit/depositions/{draft_id}",
        token=token,
        data=json.dumps(_build_metadata(tag, zenodo_path=zenodo_path, changelog_path=changelog_path)).encode(
            "utf-8"
        ),
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )

    if dry_run:
        return updated

    return _request(
        "POST",
        f"{ZENODO_API}/deposit/depositions/{draft_id}/actions/publish",
        token=token,
        timeout=timeout,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Git tag to publish, e.g. v2.0.0")
    parser.add_argument(
        "--deposition-id",
        default="21341983",
        help="Zenodo deposition ID of the latest published version",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("ZENODO_ACCESS_TOKEN", ""),
        help="Zenodo personal access token (or set ZENODO_ACCESS_TOKEN)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create and update a draft deposition without publishing",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    args = parser.parse_args(argv)

    if not args.token:
        print("Missing Zenodo token. Set ZENODO_ACCESS_TOKEN or pass --token.", file=sys.stderr)
        return 1

    result = publish_release(
        tag=args.tag,
        deposition_id=args.deposition_id,
        token=args.token,
        dry_run=args.dry_run,
        timeout=args.timeout,
    )
    output = {
        "doi": result.get("doi", ""),
        "record_id": result.get("id", ""),
        "record_url": result.get("links", {}).get("record_html"),
        "state": result.get("state", ""),
    }
    if args.dry_run:
        output["draft_url"] = result.get("links", {}).get("self")
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
