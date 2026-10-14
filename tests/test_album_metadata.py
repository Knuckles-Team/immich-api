"""Bounded projection contracts; no service, credentials or engine required."""

import unittest

from immich_api.album_metadata import album_sample, project_album


def album(number=1):
    return {
        "id": f"19abcde{number:x}-deff-4abd-91de-ffabcdabcdef",
        "albumName": "A test album",
        "assetCount": 2,
        "shared": False,
        "hasSharedLink": False,
        "createdAt": "2026-10-12T00:00:00Z",
        "updatedAt": "2026-10-12T01:00:00Z",
        "albumUsers": [{"user": {"email": "private@example.invalid"}}],
        "description": "private description",
        "key": "private share value",
        "originalPath": "/private/path",
    }


class AlbumProjectionTests(unittest.TestCase):
    def test_projection_omits_sensitive_nested_fields(self):
        result = project_album(album())
        self.assertEqual(
            set(result),
            {
                "id",
                "node_type",
                "albumName",
                "assetCount",
                "shared",
                "hasSharedLink",
                "createdAt",
                "updatedAt",
            },
        )
        self.assertNotIn("private", str(result))

    def test_sample_is_stable_bounded_and_non_authoritative(self):
        result = album_sample([album(3), album(1), album(2)], 2)
        self.assertEqual(
            [x["id"] for x in result["records"]], [album(1)["id"], album(2)["id"]]
        )
        self.assertFalse(result["complete"])
        self.assertFalse(result["authoritative"])
        self.assertFalse(album_sample([album()], 1)["authoritative"])

    def test_bounds_and_boolean_integer_are_rejected(self):
        for limit in (0, 6, True):
            with self.assertRaises(ValueError):
                album_sample([album()], limit)
        with self.assertRaises(ValueError):
            project_album(dict(album(), assetCount=True))

    def test_bad_identity_duplicates_and_timestamp_are_rejected(self):
        for invalid in (
            dict(album(), id=""),
            dict(album(), id=None),
            dict(album(), updatedAt="2026-10-12"),
        ):
            with self.assertRaises(ValueError):
                project_album(invalid)
        with self.assertRaises(ValueError):
            album_sample([album(), album()])

    def test_empty_source_is_not_authoritative(self):
        self.assertEqual(album_sample([])["records"], [])
        self.assertFalse(album_sample([])["authoritative"])


if __name__ == "__main__":
    unittest.main()
