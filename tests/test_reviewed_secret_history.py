"""The approved mock-line decision cannot suppress real evidence credentials."""

import hashlib
from pathlib import Path

import pytest

from scripts import reviewed_secret_history as policy

ROOT = Path(__file__).resolve().parents[1]
pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


def patch(lines, path=policy.SOURCE_PATH, commit="candidate"):
    return [(commit, "b/" + path, line) for line in lines]


def hits(lines, matches=lambda commit: True):
    return policy.adjudicate(lines, matches)


def test_exact_approved_line_only():
    found, reviewed = hits(patch([policy.APPROVED_LINE]))
    assert not found
    assert len(reviewed) == 1
    assert reviewed[0]["sha256"] == policy.SOURCE_SHA256


@pytest.mark.parametrize("location", ["before", "after"])
def test_real_secret_same_file_and_pattern_is_not_lost_to_deduplication(location):
    value = "credential_shape_9zQ8xP7w"
    additional = "const " + policy.FIELD + " = " + repr(value) + ";"
    lines = [policy.APPROVED_LINE, additional]
    if location == "before":
        lines.reverse()
    found, reviewed = hits(patch(lines))
    assert len(reviewed) == 1
    assert len(found) == 1
    assert value in found[0][2]


def test_other_credential_detector_still_runs_in_evidence():
    value = "ghp_" + "a1b2c3d4e5f6" * 3
    found, reviewed = hits(patch([policy.APPROVED_LINE, value]))
    assert len(reviewed) == 1
    assert len(found) == 1 and found[0][2] == value


@pytest.mark.parametrize("suffix", [".copy", "/nested", "\n"])
def test_other_paths_are_never_adjudicated(suffix):
    found, reviewed = hits(patch([policy.APPROVED_LINE], policy.SOURCE_PATH + suffix))
    assert found and not reviewed


def test_changed_blob_is_not_adjudicated():
    found, reviewed = hits(patch([policy.APPROVED_LINE]), matches=lambda commit: False)
    assert found and not reviewed


def test_changed_literal_is_not_adjudicated():
    line = policy.APPROVED_LINE.replace(repr(policy.VALUE), repr("changed_value_9zQ8"))
    found, reviewed = hits(patch([line]))
    assert found and not reviewed


def test_earlier_unknown_commit_still_fails():
    lines = patch([policy.APPROVED_LINE], commit="older") + patch(
        [policy.APPROVED_LINE], commit="reviewed"
    )
    found, reviewed = hits(lines, matches=lambda commit: commit == "reviewed")
    assert len(reviewed) == 1
    assert [hit[0] for hit in found] == ["older"]


def test_preserved_real_blob_and_exact_source_line():
    source = (ROOT / policy.SOURCE_PATH).read_bytes()
    assert hashlib.sha256(source).hexdigest() == policy.SOURCE_SHA256
    assert source.decode().splitlines()[policy.SOURCE_LINE - 1] == policy.APPROVED_LINE
    record = f"100644 blob {policy.SOURCE_BLOB}\t{policy.SOURCE_PATH}"
    assert policy.blob_matches(record, source.decode())
    assert not policy.blob_matches(record.replace("100644", "120000"), source.decode())
    assert not policy.blob_matches(record, source.decode() + "\n")


def test_unchanged_input_order_for_all_other_lines():
    original = patch(["ordinary", policy.APPROVED_LINE, "retained"])
    filtered, _ = policy.adjudicate(original, lambda commit: True)
    assert filtered == [original[0], original[2]]
