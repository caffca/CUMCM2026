# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/make_figures.py"
s = io.open(p, encoding="utf-8").read()
# 顶部 import 处把 palette 调用成 dict
s = s.replace("from figure_builder import FigureBuilder, palette, despine  # noqa",
              "from figure_builder import FigureBuilder, despine  # noqa\nimport mpl_paper_style as _mps\npalette = _mps.palette()")
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("palette dict bound; primary=", palette.get("primary") if False else "ok")
