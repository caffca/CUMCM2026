"""Small explicit-batch corpus inventory. Fetching never marks a paper read or prize-verified."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import urllib.request
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "references/design_priors"
FIELDS = "paper_id contest year group problem team_or_public_id title source_url award_evidence_url source_type provenance award_status fulltext_path identity_or_sha256 text_read_status visually_checked_pages read_status access_date license_or_reuse_note".split()
CARD_FIELDS = "paper_id problem_structure question_to_model_mapping model_choice_rationale parameter_provenance_quality claim_evidence_map cross_question_dependencies validation_target negative_or_boundary_results abstract_organization language_observations figure_roles layout_observations strongest_design_choice unsupported_or_weak_choice transferable_patterns non_transferable_details page_evidence missing_or_unread_items".split()
INDEXES = {
    "2024":"https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/2024qgdxssxjmjslwzs/",
    "2025":"https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/2025qgdxssxjmjslwzs/",
}
PRE_CONTEST_COMPLETE_TARGET = 20
POST_CONTEST_LONG_TERM_TARGET = 50


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images = [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img" and re.search(r"[A-E]\d+_页面_\d+", a.get("alt", "")):
            self.images.append((a["alt"], a["src"]))


def request(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"CUMCM-design-prior-research/1.0"}), timeout=25) as response:
        payload = response.read(16*1024*1024 + 1)
        if len(payload) > 16*1024*1024:
            raise ValueError("BLOCKED: response exceeds bounded download size")
        return payload


def load():
    path = LIBRARY / "corpus.csv"
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline=""))) if path.exists() else []


def save(rows):
    with (LIBRARY / "corpus.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def index(year):
    raw = request(INDEXES[year]).decode("utf-8")
    page = Page()
    page.feed(raw)
    urls = list(dict.fromkeys(urljoin(INDEXES[year], u) for u in page.links if f"sxjmlw_{year}qg" in u and u.endswith("shtml")))
    rows = load()
    existing = {r["source_url"] for r in rows}
    for url in urls:
        if url in existing:
            continue
        article = request(url).decode("utf-8")
        match = re.search(r"论文展示[（(]([A-E]\d+)[）)]", article)
        if not match:
            continue
        public_id = match[1]
        row = dict.fromkeys(FIELDS, "")
        row.update(paper_id=f"CUMCM{year}-{public_id}", contest="CUMCM", year=year,
                   group="本科" if public_id[0] in "ABC" else "高职高专", problem=public_id[0],
                   team_or_public_id=public_id, title=f"{year} CUMCM {public_id} 官方展示（正文标题待读）",
                   source_url=url, source_type="official_showcase", provenance="unverified", award_status="UNVERIFIED",
                   identity_or_sha256=f"CUMCM:{year}:official-display:{public_id}",
                   text_read_status="NOT_READ", read_status="INDEXED", access_date=str(date.today()),
                   license_or_reuse_note="官方公开页面；禁止未经许可转载。仅本地研究。展示身份已核实；国一等级尚需同篇证据，不自动推断。")
        rows.append(row)
        existing.add(url)
        save(rows)
        print(row["paper_id"], flush=True)


def fetch(paper_id, pages=None):
    rows = load()
    row = next(r for r in rows if r["paper_id"] == paper_id)
    page = Page()
    page.feed(request(row["source_url"]).decode("utf-8"))
    images = list(dict.fromkeys(page.images))
    directory = ROOT / "references/papers" / paper_id
    directory.mkdir(parents=True, exist_ok=True)
    def download(item):
        alt, url = item
        number = int(re.search(r"_页面_(\d+)", alt)[1])
        path = directory / f"page-{number:02}.jpg"
        if (pages is None or number in pages) and not path.exists():
            payload = request(urljoin(row["source_url"], url))
            if not payload.startswith(b"\xff\xd8") or not payload.rstrip().endswith(b"\xff\xd9"):
                raise ValueError(f"BLOCKED: not a complete JPEG page: {number}")
            path.write_bytes(payload)
    # Two bounded downloads; no crawler/service or recursive link traversal.
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(download, images))
    metadata = []
    for alt, url in images:
        number = int(re.search(r"_页面_(\d+)", alt)[1])
        path = directory / f"page-{number:02}.jpg"
        metadata.append({"physical_page":number,"url":url,"path":str(path.relative_to(ROOT)),
                         "downloaded":path.exists(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None})
    (directory / "pages.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    complete = bool(metadata) and all(m["downloaded"] for m in metadata)
    row["fulltext_path"] = str(directory.relative_to(ROOT)).replace("\\", "/") if complete else ""
    save(rows)
    print(json.dumps({"paper_id":paper_id,"source_pages":len(images),"local_pages":sum(m["downloaded"] for m in metadata),"fulltext_available":complete}, ensure_ascii=False))


def fulltext_present(row):
    if not row["fulltext_path"]:
        return False
    path = ROOT / row["fulltext_path"]
    if path.is_file():
        # Header alone accepted fake PDFs. Use the already-installed local parser.
        try:
            result = subprocess.run(["pdfinfo", str(path)], capture_output=True, timeout=10)
            return result.returncode == 0 and bool(re.search(rb"^Pages:\s*[1-9]\d*\s*$", result.stdout, re.M))
        except (OSError, subprocess.TimeoutExpired):
            return False  # unavailable parser is not a verified fulltext
    page_record = path / "pages.json"
    collector_record = path / "collector_manifest.json"
    if page_record.is_file() or collector_record.is_file():
        page_sets = []
        if page_record.is_file():
            page_sets.append(json.loads(page_record.read_text(encoding="utf-8")))
        if collector_record.is_file():
            manifest = json.loads(collector_record.read_text(encoding="utf-8"))
            if manifest.get("fulltext_complete") and len(manifest["pages"]) == manifest.get("expected_pages"):
                page_sets.append(manifest["pages"])
        return any(bool(pages) and all((ROOT/m["path"]).is_file() and m.get("downloaded") and
            hashlib.sha256((ROOT/m["path"]).read_bytes()).hexdigest() == m.get("sha256") for m in pages)
            for pages in page_sets)
    return False


def read_cards():
    path = LIBRARY / "cards.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def stats(rows=None, cards=None):
    rows = load() if rows is None else rows
    cards = read_cards() if cards is None else cards
    card_by_id = {c["paper_id"]:c for c in cards}
    unique = {}
    for r in rows:
        unique.setdefault(r["identity_or_sha256"] or r["paper_id"], r)
    all_rows = list(unique.values())
    eligible = [r for r in all_rows if r["contest"] == "CUMCM" and r["year"] in INDEXES and
                (r["provenance"] != "independently_verified" or r["award_evidence_url"]) and
                (r["provenance"],r["award_status"]) in {
                    ("user_confirmed","USER_CONFIRMED_NATIONAL_FIRST"),
                    ("independently_verified","VERIFIED_NATIONAL_FIRST")}]
    full = [r for r in all_rows if fulltext_present(r)]
    full_ids = {r["paper_id"] for r in full}
    complete = [r for r in all_rows if r["paper_id"] in full_ids and r["text_read_status"]=="BODY_READ" and
                bool(r["visually_checked_pages"]) and r["read_status"]=="COMPLETE_WITH_DECLARED_SCOPE" and
                all(k in card_by_id.get(r["paper_id"], {}) for k in CARD_FIELDS) and
                card_by_id.get(r["paper_id"], {}).get("scope_complete") is True]
    complete_ids = {r["paper_id"] for r in complete}
    design_complete = [r for r in complete if r in eligible or
                       (r["contest"] == "CUMCM" and r["year"] in INDEXES and r["source_type"] == "official_showcase")]
    return {"candidates":len(rows),"unique_identities":len(all_rows),"unique_fulltexts":len(full),
            "user_confirmed_national_first":sum(r["provenance"]=="user_confirmed" for r in eligible),
            "independently_verified_national_first":sum(r["provenance"]=="independently_verified" for r in eligible),
            "deduplicated_national_first":len(eligible),
            "text_reviewed":sum(r["text_read_status"]=="BODY_READ" for r in all_rows),
            "visual_sampled":sum(bool(r["visually_checked_pages"]) for r in all_rows),
            "complete_eligible_extractions":sum(r["paper_id"] in complete_ids for r in eligible),
            "complete_design_reads":len(design_complete),
            "official_showcase_design_reads":sum(r not in eligible for r in design_complete),
            "distribution":dict(Counter(f'{r["year"]}/{r["group"]}/{r["problem"]}' for r in all_rows)),
            "target":PRE_CONTEST_COMPLETE_TARGET,
            "pre_contest_target":PRE_CONTEST_COMPLETE_TARGET,
            "pre_contest_frozen":len(design_complete) >= PRE_CONTEST_COMPLETE_TARGET,
            "post_contest_long_term_target":POST_CONTEST_LONG_TERM_TARGET}


def validate():
    rows, cards = load(), read_cards()
    ids = {r["paper_id"] for r in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate paper_id; consolidate identities, do not count copies")
    if len({c["paper_id"] for c in cards}) != len(cards):
        raise ValueError("duplicate extraction card")
    for c in cards:
        if c["paper_id"] not in ids or set(CARD_FIELDS)-c.keys():
            raise ValueError(f"incomplete or orphan card: {c.get('paper_id')}")
        if c.get("scope_complete") and not c["page_evidence"]:
            raise ValueError("Complete extraction requires actual page evidence")
    for r in rows:
        if r["provenance"] == "user_confirmed" and r["award_status"] != "USER_CONFIRMED_NATIONAL_FIRST":
            raise ValueError("Do not relabel user-confirmed provenance as independent verification")
        if r["award_status"] == "VERIFIED_NATIONAL_FIRST" and (r["provenance"] != "independently_verified" or not r["award_evidence_url"]):
            raise ValueError("Independent verification requires same-paper award evidence")
    print("CORPUS/CARDS SCHEMA PASS")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action",required=True)
    sub.add_parser("stats")
    sub.add_parser("validate")
    i = sub.add_parser("index"); i.add_argument("--year", choices=INDEXES, required=True)
    f = sub.add_parser("fetch"); f.add_argument("--paper-id",required=True); f.add_argument("--pages",nargs="+",type=int)
    args = p.parse_args()
    if args.action == "index": index(args.year)
    elif args.action == "fetch": fetch(args.paper_id, args.pages)
    elif args.action == "validate": validate()
    else: print(json.dumps(stats(),ensure_ascii=False,indent=2))
