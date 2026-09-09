"""Only the pilot's new contracts. SYNTHETIC inputs; does not rerun the old full smoke suite."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.figures.render_figure import render
from src.visualization.export import check_plot_data, check_brief, check_comparisons
from scripts import design_priors as library


def run(work):
    work = Path(work).resolve()
    if work.exists():
        raise ValueError("Use a fresh isolated path")
    work.mkdir(parents=True)
    fixture = json.loads((Path(__file__).with_name("fixture.json")).read_text(encoding="utf-8"))
    source_path = work / "fixture.json"
    base = "0" * 40  # Test-only provenance token, NOT a modeling milestone.

    def brief(data, name):
        item = data[name]
        return dict(figure_id=name, question="SYNTHETIC", purpose="有限输入与必需比较检查",
                    supported_claim=item["supported_claims"][0], source=str(source_path),
                    unit_and_population=item["unit_and_population"], aggregation=item["aggregation"],
                    uncertainty=item["uncertainty"], required_comparison=["series:baseline", "series:main"],
                    final_width_mm=155, language="zh-CN", forbidden_inference="非真实比赛数据；不是科学命题证明")

    class Checks(unittest.TestCase):
        def test_nonfinite_shape_and_missing_policy(self):
            for field, value in (("y", [1, float("nan"), 3, 4, 5]), ("y", [1, 2]),
                                 ("y", [[1, 2, 3, 4, 5]]), ("y", [1, 2, float("inf"), 4, 5])):
                bad = copy.deepcopy(fixture)
                bad["sensitivity"]["series"][1][field] = value
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "BLOCKED"):
                    check_plot_data(bad["sensitivity"], brief(bad, "sensitivity"))
            bad = copy.deepcopy(fixture)
            bad["comparison"]["values"][0]["lower"] = float("inf")
            with self.assertRaisesRegex(ValueError, "BLOCKED"):
                check_plot_data(bad["comparison"], brief(bad, "comparison"))
            bad = copy.deepcopy(fixture)
            bad["prediction"]["predicted"] = [1]
            b = brief(bad, "prediction"); b["required_comparison"] = "none"
            with self.assertRaisesRegex(ValueError, "BLOCKED"):
                check_plot_data(bad["prediction"], b)

        def test_required_series_and_reference(self):
            bad = copy.deepcopy(fixture)
            bad["comparison"]["values"] = bad["comparison"]["values"][1:]
            with self.assertRaisesRegex(ValueError, "series:baseline"):
                check_plot_data(bad["comparison"], brief(bad, "comparison"))
            b = brief(fixture, "prediction"); b["required_comparison"] = ["reference:threshold"]
            with self.assertRaisesRegex(ValueError, "reference:threshold"):
                check_plot_data(fixture["prediction"], b)
            with self.assertRaisesRegex(ValueError, "reference:zero"):
                check_comparisons(["reference:zero"], {"reference:identity"})
            b["required_comparison"] = ["reference:identity", "reference:zero"]
            check_plot_data(fixture["prediction"], b)

        def test_declared_gap_and_normal_comparison_render(self):
            data = copy.deepcopy(fixture)
            data["sensitivity"]["series"][1]["y"][2] = None
            data["sensitivity"]["missing_data_policy"] = "gap"
            source_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            identity = hashlib.sha256(source_path.read_bytes()).hexdigest()
            for name in ("comparison", "sensitivity"):
                b = brief(data, name)
                if name == "sensitivity":
                    b.update(missing_data_policy="gap", missing_data_note="合成网格第三点缺测，仅保留断线")
                    no_note = dict(b); no_note.pop("missing_data_note")
                    with self.assertRaisesRegex(ValueError, "BLOCKED"):
                        check_plot_data(data[name], no_note)
                    all_missing = copy.deepcopy(data[name]); all_missing["series"][1]["y"] = [None]*5
                    with self.assertRaisesRegex(ValueError, "BLOCKED"):
                        check_plot_data(all_missing, b)
                bp = work / (name+".brief.json")
                bp.write_text(json.dumps(b, ensure_ascii=False), encoding="utf-8")
                result = render(source_path, identity, bp, work / "figures", base)
                self.assertIn("series:baseline", result["comparison_objects"])
                self.assertEqual(result["claim_status"], "BUILDER_TEXT_MATCH_ONLY_NOT_SCIENTIFIC_PROOF")
                if name == "sensitivity":
                    self.assertIn("保留断线", result["caption"])
            self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), identity)

        def test_claim_membership_is_not_proof(self):
            bad = copy.deepcopy(fixture)
            bad["comparison"]["supported_claims"] = ["主方案成本高于基线"]
            check_brief(bad["comparison"], brief(bad, "comparison"))
            # Intentionally passes approved-text matching. Scientific checking is separate.

        def test_fake_pdf_rejected(self):
            fake = work / "fake.pdf"
            fake.write_bytes(b"%PDF-not-a-real-file")
            self.assertFalse(library.fulltext_present({"fulltext_path":str(fake)}))

        def test_official_design_separate_from_prize(self):
            row = dict.fromkeys(library.FIELDS, "")
            row.update(paper_id="SYNTHETIC-OFFICIAL", identity_or_sha256="SYNTHETIC-OFFICIAL",
                       contest="CUMCM", year="2025", group="SYNTHETIC", problem="E",
                       source_type="official_showcase", provenance="unverified", award_status="UNVERIFIED",
                       text_read_status="BODY_READ", visually_checked_pages="SYNTHETIC 1-5",
                       read_status="COMPLETE_WITH_DECLARED_SCOPE")
            card = dict.fromkeys(library.CARD_FIELDS, "SYNTHETIC")
            card.update(paper_id=row["paper_id"], scope_complete=True)
            with patch.object(library, "fulltext_present", return_value=True):
                result = library.stats([row], [card])
                self.assertEqual(result["complete_design_reads"], 1)
                self.assertEqual(result["deduplicated_national_first"], 0)
                self.assertEqual(result["complete_eligible_extractions"], 0)
                card["scope_complete"] = False
                self.assertEqual(library.stats([row], [card])["complete_design_reads"], 0)

    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    (work / "test-result.json").write_text(json.dumps(dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), synthetic=True)), encoding="utf-8")
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True)
    run(parser.parse_args().work)
