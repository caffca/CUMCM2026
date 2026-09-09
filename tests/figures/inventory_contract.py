"""SYNTHETIC TEST: corpus accounting and explicit delivery allowlist, no real metadata edits."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import design_priors as library
from scripts.check_delivery import check


def row(paper_id, provenance, award):
    value = dict.fromkeys(library.FIELDS, "")
    value.update(paper_id=paper_id, identity_or_sha256=paper_id, contest="CUMCM", year="2025",
                 group="SYNTHETIC", problem="D", provenance=provenance, award_status=award,
                 text_read_status="BODY_READ", visually_checked_pages="SYNTHETIC 1-5",
                 read_status="COMPLETE_WITH_DECLARED_SCOPE")
    return value


class InventoryContract(unittest.TestCase):
    def test_dedup_unverified_and_no_fulltext_excluded(self):
        seed = row("SYNTHETIC-SEED", "user_confirmed", "USER_CONFIRMED_NATIONAL_FIRST")
        other = row("SYNTHETIC-WEB", "independently_verified", "VERIFIED_NATIONAL_FIRST")
        other["award_evidence_url"] = "https://example.invalid/synthetic-test-only"
        unverified = row("SYNTHETIC-UNKNOWN", "unverified", "UNVERIFIED")
        absent = row("SYNTHETIC-MISSING", "user_confirmed", "USER_CONFIRMED_NATIONAL_FIRST")
        card = dict.fromkeys(library.CARD_FIELDS, "SYNTHETIC")
        card.update(paper_id=seed["paper_id"], scope_complete=True)
        cards = [card, dict(card, paper_id=other["paper_id"]), dict(card, paper_id=unverified["paper_id"])]
        rows = [seed, copy.deepcopy(seed), other, unverified, absent]
        with patch.object(library, "fulltext_present", side_effect=lambda r:r["paper_id"] != absent["paper_id"]):
            result = library.stats(rows, cards)
        self.assertEqual(result["candidates"], 5)
        self.assertEqual(result["unique_identities"], 4)
        self.assertEqual(result["unique_fulltexts"], 3)
        self.assertEqual(result["user_confirmed_national_first"], 2)
        self.assertEqual(result["independently_verified_national_first"], 1)
        self.assertEqual(result["complete_eligible_extractions"], 2)

    def test_missing_independent_evidence_excluded(self):
        value = row("SYNTHETIC", "independently_verified", "VERIFIED_NATIONAL_FIRST")
        with patch.object(library, "fulltext_present", return_value=False):
            self.assertEqual(library.stats([value], [])["deduplicated_national_first"], 0)

    def test_incomplete_card_not_counted(self):
        value = row("SYNTHETIC", "user_confirmed", "USER_CONFIRMED_NATIONAL_FIRST")
        with patch.object(library, "fulltext_present", return_value=True):
            self.assertEqual(library.stats([value], [{"paper_id":"SYNTHETIC", "scope_complete":True}])["complete_eligible_extractions"], 0)

    def test_delivery_source_allowed(self):
        result = check(ROOT, [{"path":"src/visualization/style.py", "purpose":"source", "reuse_allowed":True}])
        self.assertFalse(result["archive_created"])

    def test_delivery_denied_paths_and_missing_permission(self):
        for path in (".venv/pyvenv.cfg", ".git/config", "references/design_priors/INDEX.md", "../secret.txt"):
            with self.assertRaisesRegex(ValueError, "BLOCKED"):
                check(ROOT, [{"path":path, "purpose":"SYNTHETIC", "reuse_allowed":True}])
        with self.assertRaisesRegex(ValueError, "BLOCKED"):
            check(ROOT, [{"path":"src/visualization/style.py", "purpose":"source", "reuse_allowed":False}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
