# -*- coding: utf-8 -*-
import io, json, os
p = "code/prod/make_figures.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('fb.save(fig, [{"ax": ax, "panel_id": "A"}], caption="时频占用栅格与冲突单元", generator="code/prod/make_figures.py")',
              'fb.save(fig, [{"ax": ax, "panel_id": "A"}], out_dir="figures/drafts", caption="时频占用栅格与冲突单元", generator="code/prod/make_figures.py")')
s = s.replace('fb.save(fig, [{"ax": ax, "panel_id": "A"}], caption="冲突度分布", generator="code/prod/make_figures.py")',
              'fb.save(fig, [{"ax": ax, "panel_id": "A"}], out_dir="figures/drafts", caption="冲突度分布", generator="code/prod/make_figures.py")')
s = s.replace('fb.save(fig, [{"ax": ax, "panel_id": "A"}], caption="冲突对类别构成", generator="code/prod/make_figures.py")'.replace("图X ", ""),
              'fb.save(fig, [{"ax": ax, "panel_id": "A"}], out_dir="figures/drafts", caption="冲突对类别构成", generator="code/prod/make_figures.py")')
import re
s = re.sub(r'fb\.save\(fig, (\[[^\]]+\])\s*,\s*caption=', r'fb.save(fig, \1, out_dir="figures/drafts", caption=', s)
# manifest 源改读 drafts 草案
s = s.replace('m = json.load(open("figures/figure_manifest.json", encoding="utf-8"))',
              'mp = "figures/figure_manifest.json"\n    m = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else []')
s = s.replace('    print("figures written:", len(os.listdir("figures")))',
              '''    reqs = {x["id"]: x for x in json.load(open("reports/FIGURE_REQUIREMENTS.json", encoding="utf-8"))["figures"]}
    dm = []
    for f in sorted(os.listdir("figures/drafts")):
        if f.endswith(".pdf"):
            fid = f[:-4]
            meta = json.load(open(f"figures/drafts/{fid}.meta.json", encoding="utf-8"))
            rq = reqs.get(fid, {})
            dm.append({"id": fid, "question_id": rq.get("question_id"), "status": "drafted",
                       "files": [f"figures/drafts/{fid}.pdf"],
                       "meta": f"figures/drafts/{fid}.meta.json",
                       "story": {"main_message": rq.get("main_message", ""), "claim_bind": rq.get("claim_bind", [])},
                       "panels": rq.get("panels", []), "data_source": rq.get("data_source", ""),
                       "source": {"generator": "code/prod/make_figures.py"},
                       "source_hash": meta.get("source_hash"), "caption": meta.get("caption", "")})
    json.dump(dm, open("figures/draft_figure_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("draft figures written:", len(dm))''')
io.open(p, "w", encoding="utf-8").write(s)
import py_compile
py_compile.compile(p, doraise=True)
print("make_figures -> drafts OK")
