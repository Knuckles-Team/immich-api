"""Apply the approved exception to four exact, immutable upstream artifacts.

The shared @main hook environment still supplies the scanner, thresholds,
index reader, before/after comparison and finding renderer. Only two pinned
TypeScript evidence files are removed from its staged complexity inventory.
All four pins are checked in both the index and working tree on both hook stages.
"""

import hashlib
import sys
import tempfile
from pathlib import Path

PINS = {
    "api-spec/immich.openapi.json": "7db8383741eeb5c5c8c87a6221cd1cdd1206c8b1190b83363c64223a00bb020b",
    "api-spec/provider-source/LICENSE": "a3bad629f67f442b23b5224419e49edafc32e6b9c876b89464f7aafe6091ccde",
    "api-spec/provider-source/server/src/services/auth.service.ts": "58c8a233f7637785d2d0b1c10c16e75097041310167badebea5134d149526dd1",
    "api-spec/provider-source/server/src/utils/misc.ts": "55f456af4c6cbd12615e48588c92dd974aa0a721ccb321b5320bca6ab810c4ba",
}
COMPLEXITY_EXEMPT = frozenset(path for path in PINS if path.endswith(".ts"))
EOF_EXEMPT = frozenset(PINS) - COMPLEXITY_EXEMPT


def verify_bytes(relative, content):
    if content is None or hashlib.sha256(content).hexdigest() != PINS[relative]:
        raise ValueError(f"Pinned upstream evidence changed or missing: {relative}")


def verify_pins(root, read_index):
    for relative in PINS:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Pinned evidence must be a regular file: {relative}")
        path.resolve().relative_to(root.resolve())
        verify_bytes(relative, path.read_bytes())
        verify_bytes(relative, read_index(relative))


def selected_paths(paths, supported_suffixes):
    return [
        path
        for path in paths
        if path not in COMPLEXITY_EXEMPT
        and Path(path).suffix.lower() in supported_suffixes
    ]


def index_bytes(root, relative):
    from pipelines_hooks.core.gitenv import blob_text

    value = blob_text(root, f":{relative}")
    return None if value is None else value.encode("utf-8")


def main():
    from pipelines_hooks.complexity import cccc
    from pipelines_hooks.complexity.staged import ADVICE, check_file
    from pipelines_hooks.core.gitenv import repo_root, staged_paths
    from pipelines_hooks.core.tools import verified

    root = repo_root(Path.cwd())
    verify_pins(root, lambda relative: index_bytes(root, relative))
    files = selected_paths(staged_paths(root), cccc.SUPPORTED_SUFFIXES)
    executable = verified("cccc")
    print(
        f"Pinned evidence verified; shared complexity scans {len(files)} staged files.",
        file=sys.stderr,
    )
    with tempfile.TemporaryDirectory(prefix="immich-evidence-complexity-") as raw:
        findings = [
            finding
            for relative in files
            for finding in check_file(
                root, relative, executable=executable, scratch=Path(raw)
            )
        ]
    if findings:
        print(ADVICE, file=sys.stderr)
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
