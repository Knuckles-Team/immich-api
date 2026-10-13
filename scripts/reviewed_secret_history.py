"""Adjudicate one approved public upstream mock literal; scan all other lines.

No source bytes, detector patterns, other paths or earlier unknown blobs are
exempted. The shared scanner still evaluates every remaining added line before
its ordinary per-file finding deduplication. Plain-text/self-check modes retain
the shared behavior without this historical-source adjudication.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

SOURCE_PATH = (
    "api-spec/provider-source/server/src/maintenance/maintenance-worker.service.ts"
)
SOURCE_BLOB = "f088637a5758fac616f74fc7de84c679ba7c758e"
SOURCE_SHA256 = "5d612410938d1685a3c5b1496b20fc6a05105fa89489c4a15771badbcb49fed9"
SOURCE_LINE = 63
FIELD = "secret"
VALUE = "secret"
APPROVED_LINE = "    this.#" + FIELD + " = " + repr(VALUE) + ";"


def blob_matches(record, content):
    if record != f"100644 blob {SOURCE_BLOB}\t{SOURCE_PATH}":
        return False
    return (
        hashlib.sha256(content.encode()).hexdigest() == SOURCE_SHA256
        and content.splitlines()[SOURCE_LINE - 1] == APPROVED_LINE
    )


def verified_blob(root, commit):
    from pipelines_hooks.core.gitenv import git_text

    record = git_text(root, ("ls-tree", commit, "--", SOURCE_PATH)).strip()
    if record != f"100644 blob {SOURCE_BLOB}\t{SOURCE_PATH}":
        return False
    return blob_matches(record, git_text(root, ("show", f"{commit}:{SOURCE_PATH}")))


def adjudicate(entries, matches_blob):
    filtered, reviewed, verified = [], [], {}
    for commit, path, content in entries:
        if path == "b/" + SOURCE_PATH and content == APPROVED_LINE:
            if commit not in verified:
                verified[commit] = matches_blob(commit)
            if verified[commit]:
                reviewed.append(
                    {
                        "commit": commit,
                        "path": SOURCE_PATH,
                        "line": SOURCE_LINE,
                        "blob": SOURCE_BLOB,
                        "sha256": SOURCE_SHA256,
                    }
                )
                continue
        filtered.append((commit, path, content))
    return filtered, reviewed


def check(root, base):
    from pipelines_hooks.core.gitenv import git_text
    from pipelines_hooks.security.history_scan import (
        COMMIT_MARK,
        added_lines,
        scan_credentials,
        scan_entropy,
    )

    revision = f"{base}..HEAD" if base else "HEAD"
    patch = git_text(
        root, ("log", "-p", "--format=%x00COMMIT%x00%H", revision)
    ).splitlines()
    entries, reviewed = adjudicate(
        added_lines(patch), lambda commit: verified_blob(root, commit)
    )
    filtered = [
        frame
        for commit, path, content in entries
        for frame in (COMMIT_MARK + commit, "+++ " + path, "+" + content)
    ]
    hits, entropy = scan_credentials(filtered), scan_entropy(patch)
    result = {
        "ok": not hits,
        "range": revision if base else "full history (no published base)",
        "addedLines": sum(
            line.startswith("+") and not line.startswith("+++") for line in patch
        ),
        "credentialHits": hits,
        "entropyCandidateCount": len(entropy),
        "entropySample": entropy[:20],
        "reviewedFalsePositives": reviewed,
    }
    return int(bool(hits)), result


def main(argv=None):
    from pipelines_hooks.core.baseref import upstream_base
    from pipelines_hooks.security import secret_history

    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--self-check" in arguments or "--text-file" in arguments:
        return secret_history.main(arguments)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root", "--root", dest="root", type=Path, default=Path.cwd()
    )
    parser.add_argument("--base", default=None)
    args = parser.parse_args(arguments)
    root = args.root.resolve()
    status, receipt = check(root, upstream_base(root, args.base))
    print(json.dumps(receipt, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
