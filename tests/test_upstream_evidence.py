"""Approved evidence exceptions never broaden into connector-code exclusions."""

import re
from pathlib import Path

import pytest
import yaml

from scripts import upstream_evidence as evidence

ROOT = Path(__file__).resolve().parents[1]
pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


@pytest.fixture
def pinned_tree(tmp_path):
    index = {}
    for relative in evidence.PINS:
        data = (ROOT / relative).read_bytes()
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        index[relative] = data
    return tmp_path, index


def test_original_index_and_worktree_pins_pass(pinned_tree):
    root, index = pinned_tree
    evidence.verify_pins(root, index.get)


@pytest.mark.parametrize("relative", evidence.PINS)
@pytest.mark.parametrize("surface", ["index", "worktree"])
def test_changed_bytes_fail_before_exclusion(pinned_tree, relative, surface):
    root, index = pinned_tree
    changed = index[relative] + b"\n"
    if surface == "index":
        index[relative] = changed
    else:
        (root / relative).write_bytes(changed)
    with pytest.raises(ValueError, match="Pinned upstream evidence changed"):
        evidence.verify_pins(root, index.get)


@pytest.mark.parametrize("relative", evidence.PINS)
def test_missing_index_evidence_fails(pinned_tree, relative):
    root, index = pinned_tree
    del index[relative]
    with pytest.raises(ValueError, match="missing"):
        evidence.verify_pins(root, index.get)


def test_symlink_cannot_replace_pinned_file(pinned_tree):
    root, index = pinned_tree
    relative = "api-spec/immich.openapi.json"
    target = root / relative
    replacement = root / "same-bytes.json"
    target.rename(replacement)
    target.symlink_to(replacement)
    with pytest.raises(ValueError, match="regular file"):
        evidence.verify_pins(root, index.get)


def test_only_exact_two_complexity_paths_are_removed():
    assert evidence.COMPLEXITY_EXEMPT == {
        "api-spec/provider-source/server/src/services/auth.service.ts",
        "api-spec/provider-source/server/src/utils/misc.ts",
    }
    assert evidence.EOF_EXEMPT == {
        "api-spec/immich.openapi.json",
        "api-spec/provider-source/LICENSE",
    }
    protected = [
        "immich_api/openapi_runtime.py",
        "scripts/measure_operation_parity.py",
        "scripts/upstream_evidence.py",
        "tests/test_upstream_evidence.py",
        "api-spec/provider-source/server/src/services/new.service.ts",
        "api-spec/provider-source/server/src/services/auth.service.ts.copy.ts",
        "prefix/api-spec/provider-source/server/src/services/auth.service.ts",
    ]
    paths = [*evidence.COMPLEXITY_EXEMPT, *protected]
    assert evidence.selected_paths(paths, {".py", ".ts"}) == protected


def test_hook_policy_preserves_main_security_and_exact_eof_scope():
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    assert "exclude" not in config
    repositories = {item["repo"]: item for item in config["repos"]}
    pipeline = repositories["https://github.com/Knuckles-Team/pipelines"]
    assert pipeline["rev"] == "main"
    assert "exclude" not in pipeline
    hooks = {hook["id"]: hook for hook in pipeline["hooks"]}
    assert hooks["security-sanitizer"] == {"id": "security-sanitizer"}
    assert hooks["complexity-staged"] == {
        "id": "complexity-staged",
        "entry": "python scripts/upstream_evidence.py",
        "stages": ["pre-commit", "pre-push"],
    }
    formatting = repositories["https://github.com/pre-commit/pre-commit-hooks"]
    eof = next(
        hook for hook in formatting["hooks"] if hook["id"] == "end-of-file-fixer"
    )
    pattern = re.compile(eof["exclude"])
    for relative in evidence.EOF_EXEMPT:
        assert pattern.search(relative)
        assert not pattern.search("prefix/" + relative)
        assert not pattern.search(relative + ".copy")
        assert not pattern.search(relative + "\n")
    for relative in [
        *evidence.COMPLEXITY_EXEMPT,
        "immich_api/openapi_runtime.py",
        "scripts/upstream_evidence.py",
    ]:
        assert not pattern.search(relative)
