"""Exact evidence admission preserves mixed and implementation clone findings."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

from scripts import generated_schema_clones as wrapper
from scripts import verify_generated_schemas as verifier

ROOT = Path(__file__).resolve().parents[1]
pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


@pytest.fixture
def snapshot(tmp_path):
    target = tmp_path / "snapshot"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(
            ".git", ".pytest_cache", "__pycache__", ".ruff_cache", ".kiss"
        ),
    )
    return target


def test_allowlist_is_exact_and_has_no_implementation_paths():
    policy = verifier.load_policy(ROOT)
    assert len(policy["artifacts"]) == 14
    assert policy["regenerated_schemas"] == [verifier.INVENTORY]
    assert all(
        path.endswith((".json", "/auth.service.ts")) for path in policy["artifacts"]
    )
    assert not any(
        path.startswith(("scripts/", "tests/")) for path in policy["artifacts"]
    )
    assert set(
        path for path in policy["artifacts"] if path.startswith("immich_api/")
    ) == {verifier.INVENTORY}


def test_both_verified_members_required():
    verified = verifier.load_policy(ROOT)["artifacts"]
    evidence = "api-spec/immich.provider-evidence.json"
    paths = [
        (verifier.INVENTORY, verifier.INVENTORY),
        (verifier.INVENTORY, evidence),
        ("immich_api/openapi_runtime.py", verifier.INVENTORY),
        ("immich_api/openapi_runtime.py", "scripts/verify_generated_schemas.py"),
        ("validation/new-evidence.json", evidence),
        ("api-spec/provider-source/server/src/services/new.service.ts", evidence),
    ]
    keys = [("json", str(index), pair, 0) for index, pair in enumerate(paths)]
    pairs = dict.fromkeys(keys, ())
    assert set(wrapper.retain_pairs(pairs, verified)) == set(keys[2:])
    assert wrapper.retain_pairs(pairs, {}) == pairs


@pytest.mark.parametrize("mutation", ["extra-artifact", "changed-pin", "extra-schema"])
def test_policy_cannot_broaden_or_repin(snapshot, mutation):
    path = snapshot / verifier.MANIFEST
    policy = json.loads(path.read_text())
    if mutation == "extra-artifact":
        policy["artifacts"]["immich_api/openapi_runtime.py"] = "0" * 64
    elif mutation == "changed-pin":
        policy["artifacts"][verifier.INVENTORY] = "0" * 64
    else:
        policy["regenerated_schemas"].append("validation/new.json")
    path.write_text(json.dumps(policy))
    with pytest.raises(ValueError, match="hash mismatch"):
        verifier.load_policy(snapshot)


@pytest.mark.parametrize("relative", list(verifier.load_policy(ROOT)["artifacts"]))
def test_every_evidence_byte_pin_is_enforced(snapshot, relative):
    path = snapshot / relative
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        verifier.load_policy(snapshot)


@pytest.mark.parametrize(
    "relative",
    [
        "api-spec/immich.openapi.json",
        "immich_api/parity/openapi_parity.py",
        "scripts/generate_tool_schemas.py",
    ],
)
def test_changed_source_compiler_or_native_writer_fails(snapshot, relative):
    policy = verifier.load_policy(snapshot)
    path = snapshot / relative
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        verifier.verify_provenance(snapshot, policy)


def test_unlisted_provider_source_is_still_verified(snapshot):
    policy = verifier.load_policy(snapshot)
    relative = "api-spec/provider-source/server/src/controllers/oauth.controller.ts"
    path = snapshot / relative
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        verifier.regenerated_inventory(snapshot, policy)


def test_missing_historical_manifest_admits_nothing(tmp_path):
    assert wrapper.verified_artifacts(tmp_path, ROOT) == {}


def test_special_artifact_is_rejected(snapshot):
    path = snapshot / verifier.INVENTORY
    replacement = snapshot / "same-bytes.json"
    path.rename(replacement)
    path.symlink_to(replacement)
    with pytest.raises(ValueError, match="regular file"):
        verifier.load_policy(snapshot)


def test_real_exact_tree_regeneration_native_freshness_and_no_mutation(
    snapshot, monkeypatch
):
    monkeypatch.setenv("GENERATED_SCHEMA_PYTHON", sys.executable)
    before = wrapper.tree_state(snapshot)
    assert (
        wrapper.verified_artifacts(snapshot, ROOT)
        == verifier.load_policy(snapshot)["artifacts"]
    )
    assert wrapper.tree_state(snapshot) == before


def test_main_and_security_policy_remain_in_force():
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    pipeline = next(
        item for item in config["repos"] if item["repo"].endswith("/pipelines")
    )
    assert pipeline["rev"] == "main"
    hooks = {hook["id"]: hook for hook in pipeline["hooks"]}
    assert hooks["security-sanitizer"] == {"id": "security-sanitizer"}
    assert (
        hooks["jscpd-differential"]["entry"]
        == "python scripts/generated_schema_clones.py differential"
    )
    assert (
        hooks["jscpd-census"]["entry"]
        == "python scripts/generated_schema_clones.py census"
    )
    assert (
        hashlib.sha256((ROOT / verifier.MANIFEST).read_bytes()).hexdigest()
        == verifier.MANIFEST_SHA256
    )
