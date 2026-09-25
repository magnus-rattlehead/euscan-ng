"""Check the latest published stable GitHub release from package metadata."""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import portage

from euscan import mangling, output

HANDLER_NAME = "github"
CONFIDENCE = 100
PRIORITY = 100


def can_handle(pkg, url=None):
    return False  # Selected by the github remote-id in metadata.xml.


def scan_pkg(pkg, options):
    repository = (options.get("data") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid GitHub remote-id in metadata.xml")
    if repository.split("/")[1] in (".", ".."):
        raise ValueError("invalid GitHub repository name")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "euscan-ng"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(
        f"https://api.github.com/repos/{repository}/releases/latest", headers=headers
    )
    output.einfo(f"Checking latest stable GitHub release: {repository}")
    try:
        with urlopen(request, timeout=15) as response:
            release = json.load(response)
    except HTTPError as error:
        status = error.code
        error.close()
        raise ValueError(f"GitHub {repository}: HTTP {status}") from None
    except (URLError, OSError):
        raise ValueError(f"GitHub {repository}: request failed") from None
    if not isinstance(release, dict):
        raise ValueError("invalid GitHub release response")
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("GitHub did not return a published stable release")
    tag, url = release.get("tag_name"), release.get("html_url")
    if not isinstance(tag, str) or not tag or not isinstance(url, str) or not url:
        raise ValueError("GitHub release is missing its tag or URL")
    version = mangling.mangle_version(re.sub(r"^v(?=[0-9])", "", tag), options)
    if not portage.versions.ververify(version):
        raise ValueError(f"unrecognized GitHub release version: {tag}")
    _, current, _ = portage.pkgsplit(pkg.cpv)
    if portage.versions.vercmp(version, current) <= 0:
        return []
    return [(url, version, HANDLER_NAME, CONFIDENCE)]
