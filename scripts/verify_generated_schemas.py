"""Verify only the exact approved generated and evidence artifacts, offline."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MANIFEST = ".config/generated-schema-policy.json"
MANIFEST_SHA256 = "dd1149e1c804a7684863c8e1ccd095ad19a3666d96199ac5b55007ce20487e96"
INVENTORY = "immich_api/openapi_inventory.json"


def regular_bytes(root, relative):
    path = root / relative
    path.resolve().relative_to(root.resolve())
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Verified artifact must be a regular file: {relative}")
    return path.read_bytes()


def require_hash(root, relative, expected):
    value = regular_bytes(root, relative)
    if hashlib.sha256(value).hexdigest() != expected:
        raise ValueError(f"Verified artifact hash mismatch: {relative}")
    return value


def load_policy(root):
    policy = json.loads(require_hash(root, MANIFEST, MANIFEST_SHA256))
    for relative, expected in policy["artifacts"].items():
        require_hash(root, relative, expected)
    return policy


def verify_provenance(root, policy):
    provenance = policy["provenance"]
    generation = json.loads(regular_bytes(root, provenance["generation_receipt"]))
    if generation["builder_revision"] != provenance["builder_revision"]:
        raise ValueError("Compiler revision differs from approved provenance")
    for relative, expected in generation["generated_files"].items():
        if relative != "mcp/__init__.py":
            require_hash(root, "immich_api/" + relative, expected)
    runtime = json.loads(regular_bytes(root, provenance["runtime_receipt"]))
    for relative, expected in runtime["runtime_source_sha256"].items():
        require_hash(root, relative, expected)
    writer = "scripts/generate_tool_schemas.py"
    require_hash(
        root, writer, generation["all_file_changes"][writer]["after"]["sha256"]
    )
    require_hash(root, "api-spec/immich.openapi.json", provenance["raw_source_sha256"])
    require_hash(
        root,
        provenance["provider_overlay_path"],
        provenance["provider_overlay_sha256"],
    )


def regenerated_inventory(root, policy):
    sys.path.insert(0, str(root / "immich_api/parity"))
    from openapi_parity import source_context, verify_contract

    provenance = policy["provenance"]
    source = regular_bytes(root, "api-spec/immich.openapi.json")
    document = json.loads(source)
    options = {
        "source_bytes": source,
        "overlay_bytes": regular_bytes(root, provenance["provider_overlay_path"]),
        "expected_overlay_sha256": provenance["provider_overlay_sha256"],
        "evidence_root": root / "api-spec/provider-source",
    }
    _, inventory = source_context(document, provenance["raw_source_sha256"], **options)
    contract = json.loads(regular_bytes(root, "immich_api/openapi_contract.json"))
    verify_contract(document, contract, provenance["raw_source_sha256"], **options)
    return (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode()


def verify_native_schemas(root):
    result = subprocess.run(
        [sys.executable, str(root / "scripts/generate_tool_schemas.py"), "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    if result.returncode:
        raise ValueError("Native schema freshness verification failed")


def verify(root):
    policy = load_policy(root)
    verify_provenance(root, policy)
    first = regenerated_inventory(root, policy)
    second = regenerated_inventory(root, policy)
    if first != second or first != regular_bytes(root, INVENTORY):
        raise ValueError("Approved inventory does not regenerate byte-identically")
    verify_native_schemas(root)
    return {"version": 1, "verified_artifacts": policy["artifacts"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    root = parser.parse_args().root.resolve()
    print(json.dumps(verify(root), sort_keys=True))


if __name__ == "__main__":
    main()
