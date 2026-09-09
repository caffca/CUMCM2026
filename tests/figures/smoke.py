"""SYNTHETIC TEST. All generated artifacts stay in an isolated scratch repository."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.figures.render_figure import render
from src.visualization.export import read_frozen, check_brief
from src.visualization.style import apply_competition_style, select_chinese_font, PALETTE
import matplotlib as mpl
import matplotlib.pyplot as plt


def run(work):
    work = Path(work).resolve()
    if work.exists():
        raise ValueError("Use a fresh scratch path; never overwrite an existing repository")
    work.mkdir(parents=True)
    subprocess.run(["git", "init", "-b", "main", str(work)], check=True, capture_output=True)
    frozen = work / "inputs"
    frozen.mkdir()
    source = frozen / "fixture.json"
    shutil.copy2(Path(__file__).with_name("fixture.json"), source)
    # Local synthetic fixture commit belongs only to the scratch repository.
    subprocess.run(["git", "-C", str(work), "add", "inputs/fixture.json"], check=True)
    subprocess.run(["git", "-C", str(work), "-c", "user.name=Synthetic Test", "-c", "user.email=synthetic@example.invalid", "commit", "-m", "test: synthetic fixture only"], check=True, capture_output=True)
    base = subprocess.check_output(["git", "-C", str(work), "rev-parse", "HEAD"], text=True).strip()
    identity = hashlib.sha256(source.read_bytes()).hexdigest()
    data = json.loads(source.read_text(encoding="utf-8"))
    reports = {}
    for name in ("comparison", "sensitivity", "prediction", "framework"):
        item = data[name]
        brief = dict(figure_id=name, question="SYNTHETIC", purpose={"comparison":"比较给定成本", "sensitivity":"观察网格敏感性", "prediction":"检查预测与残差", "framework":"说明问题依赖"}[name],
                     supported_claim=item["supported_claims"][0], source=str(source),
                     unit_and_population=item["unit_and_population"], uncertainty=item["uncertainty"], aggregation=item["aggregation"],
                     required_comparison=(["series:baseline", "series:main"] if name in ("comparison", "sensitivity") else
                                          ["reference:identity", "reference:zero"] if name == "prediction" else "none"),
                     final_width_mm=155, language="zh-CN",
                     forbidden_inference="不代表真实比赛结果、统计显著性、因果或全局最优")
        brief_path = frozen / (name + ".brief.json")
        brief_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
        first = render(source, identity, brief_path, work / "figures", base)
        second = render(source, identity, brief_path, work / "repeat", base)
        assert first == second
        reports[name] = first

    class ContractTests(unittest.TestCase):
        def test_semantic_colors_and_size(self):
            apply_competition_style()
            self.assertEqual(mpl.rcParams["axes.prop_cycle"].by_key()["color"][0], PALETTE["main"])
            self.assertAlmostEqual(mpl.rcParams["figure.figsize"][0] * 25.4, 155)
        def test_missing_input(self):
            with self.assertRaisesRegex(ValueError, "BLOCKED"):
                read_frozen(frozen / "missing.json", identity)
        def test_stale_input(self):
            with self.assertRaisesRegex(ValueError, "STALE"):
                read_frozen(source, "0" * 64)
        def test_unit_and_interval_mutations(self):
            valid = json.loads((frozen / "comparison.brief.json").read_text(encoding="utf-8"))
            for key, wrong in (("unit_and_population", "美元"), ("uncertainty", "95% CI"), ("aggregation", "擅自改为样本平均"), ("supported_claim", "主方案全局最优")):
                bad = copy.deepcopy(valid)
                bad[key] = wrong
                with self.assertRaisesRegex(ValueError, "BLOCKED"):
                    check_brief(data["comparison"], bad)
        def test_missing_glyph(self):
            with self.assertRaisesRegex(ValueError, "BLOCKED"):
                select_chinese_font("\U0010ffff")
        def test_input_unchanged_and_figures_closed(self):
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), identity)
            self.assertEqual(plt.get_fignums(), [])
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests))
    reports["test_summary"] = {"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"synthetic":True}
    (work / "smoke-evidence.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(work)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True)
    run(parser.parse_args().work)
