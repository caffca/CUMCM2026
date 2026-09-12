"""Audit exactness of Q4 resource-cell cliques against state conflict edges."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from d_problem.io import load_plans  # noqa: E402
from d_problem.q4_candidates import (  # noqa: E402
    generate_all_candidates,
    generate_cell_cliques,
    generate_conflict_edges,
)


def audit(input_path: Path, horizon: int) -> dict[str, object]:
    plans = load_plans(input_path)
    grouped, flat = generate_all_candidates(plans, horizon=horizon)
    edges = {tuple(sorted(edge)) for edge in generate_conflict_edges(grouped)}
    by_index = {candidate.index: candidate for candidate in flat}
    cell_pairs: set[tuple[int, int]] = set()
    cliques = generate_cell_cliques(flat)
    for clique in cliques:
        for left, right in combinations(clique, 2):
            if by_index[left].plan.plan_id == by_index[right].plan.plan_id:
                continue
            cell_pairs.add(tuple(sorted((left, right))))
    missing = edges - cell_pairs
    extra = cell_pairs - edges
    return {
        "horizon": horizon,
        "candidate_state_count": len(flat),
        "state_conflict_edges": len(edges),
        "cell_clique_count": len(cliques),
        "cross_plan_cell_pairs": len(cell_pairs),
        "missing_edge_count": len(missing),
        "extra_pair_count": len(extra),
        "ok": not missing and not extra,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "D题/附件/附件1.xlsx")
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "outputs/q4/cell_edge_equivalence.json"
    )
    args = parser.parse_args()
    report = audit(args.input, args.horizon)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
