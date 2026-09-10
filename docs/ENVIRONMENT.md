# Environment

## Current workspace override — 2026-09-10

- Actual repository: `C:\Users\ysw\Desktop\CUMCM2026`.
- The historical verification notes below contain older `E:\CUMCM2026` paths; they are evidence
  of earlier checks, not current paths.
- The repository `.venv\pyvenv.cfg` currently points to missing
  `C:\Program Files\Python312\python.exe`; re-check or repair the environment before using it.

Last verified: 2026-09-09 (four-page synthetic publication chain; earlier core inventory retained)
Status: **Core environment retained; Windows plot + multi-page Chinese PDF VERIFIED; CTeX NOT READY**

## Canonical runtime

- Default runtime: `E:\CUMCM2026\.venv`
- Activation: `.\.venv\Scripts\Activate.ps1`
- Python executable: `E:\CUMCM2026\.venv\Scripts\python.exe`
- Python version: 3.12.6
- System Python and existing Conda environments were not modified.

Use the repository `.venv` by default during the competition. The machine also has
Conda 24.9.2 at `E:\anaconda` with unrelated environments; none is the project default.

## Core scientific packages — READY

| Package | Version |
|---|---:|
| NumPy | 2.5.2 |
| Pandas | 3.0.5 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.1 |
| scikit-learn | 1.9.0 |
| statsmodels | 0.14.6 |
| SymPy | 1.14.0 |
| NetworkX | 3.6.1 |

## Optimization — READY

- CVXPY 1.9.2; available backends include CLARABEL, HIGHS, OSQP and SCS.
- HiGHS Python bindings 1.15.1; a small LP solved successfully through CVXPY.
- PuLP 3.3.2 with its bundled CBC executable; a small LP solved successfully.
- OR-Tools 9.15.6755; GLOP small LP solved successfully.

## ML / Excel / plotting — READY

- XGBoost 3.4.1 and LightGBM 4.7.0: installed and importable; no training run performed.
- Excel I/O: openpyxl 3.1.5 and XlsxWriter 3.2.9; Chinese-column CSV/XLSX round trip passed.
- Attachment compatibility: xlrd 2.0.2 for legacy `.xls` reading; h5py 3.16.0 for HDF5/
  MATLAB v7.3-compatible data; python-docx 1.2.0 for DOCX reading/writing.
- Pillow 12.3.0, PyYAML 6.0.3 and tqdm 4.70.0 installed.
- Matplotlib generated non-empty PNG and PDF smoke figures successfully.
- Confirmed useful fonts: SimHei, SimSun, Noto Sans SC, SimKai and FangSong families.

## External tools

| Capability | Status | Version / backend |
|---|---|---|
| Git | READY | 2.45.1.windows.1 |
| WSL | AVAILABLE | Ubuntu-24.04 and Debian listed |
| XeLaTeX / PDFLaTeX / latexmk | AVAILABLE | MiKTeX 25.12 / MiKTeX-XeTeX 4.16 |
| CTeX end-to-end compile | NOT READY | 2026-09-09: xelatex format starts, but `ctexart.cls` missing; installer disabled |
| Poppler render / inspect | READY | `pdftoppm` and `pdfinfo` 26.07.0 |
| MATLAB | NOT FOUND | not installed / not on PATH |
| R / Rscript | NOT FOUND | not installed / not on PATH |
| Gurobi / CPLEX | NOT FOUND | no executable or Python binding found |
| SCIP / GLPK / standalone CBC | NOT FOUND | no executable found; PuLP CBC is usable |
| Graphviz / Pandoc / Excel application | NOT FOUND | Python I/O and NetworkX remain available |

## Tier C — optional, on demand

Not prepared because they are not needed for the core competition environment:

- PyTorch, TensorFlow, OpenCV, scikit-image;
- GeoPandas, Shapely, Prophet, CatBoost;
- gurobipy and docplex;
- GPU/CUDA stack, MATLAB, R, commercial solvers and extra GIS tooling.

These are not blockers. Install only if a future problem specifically requires them.

## Historical verification — 2026-08-25

- Numerical: NumPy matrix operation, SciPy optimization and SymPy equation solve passed.
- Data: CSV/XLSX write/read with Chinese columns passed.
- Statistics/ML: sklearn linear/logistic regression and statsmodels OLS passed.
- Graph: NetworkX shortest path passed.
- Optimization: CVXPY/CLARABEL, PuLP/CBC and OR-Tools/GLOP small LPs passed.
- Plotting: Matplotlib PNG/PDF export passed.
- Attachment compatibility: xlrd import/version, h5py HDF5 round trip and python-docx Chinese DOCX round trip passed.
- CTeX: minimal Chinese document compile failed during MiKTeX `xelatex.fmt` generation; XeLaTeX executable remains available.
- `python -m pip check`: passed — no broken requirements found.

Those historical test artifacts were removed after that smoke suite. `.venv/` is local
and ignored by Git. The 2026-09-09 test evidence below is retained in `tmp/`.

## Competition Environment Freeze

The core CUMCM environment is prepared and frozen for normal competition use.

Do not proactively install additional packages during the competition.

New dependencies may be added only when the selected problem requires a capability
that is not reasonably available from the current stack.

## Safety

- Activate only `E:\CUMCM2026\.venv` for this repository.
- No system Python, Conda environment, PATH, CUDA, MATLAB, R, TeX or commercial solver was modified.
- Do not commit `.venv/`, pip cache, smoke files or temporary logs.

## 2026-09-09 plotting/publication verification

User Windows machine: repository Python 3.12.6 ran four frozen SYNTHETIC TEST plots,
repeat-value checks and six contract tests. Matplotlib resolved an installed Chinese font
with explicit glyph coverage; PDF width is 155mm. All four PNGs were actually inspected.

CTeX command with `--disable-installer` failed on missing `ctexart.cls`; no install attempted.
Verified alternative: local bundled Python at
`C:\Users\zyy17\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
uses ReportLab + pypdf, then local Poppler renders the composed page. SimHei plus Segoe UI
per-glyph fallback fixes the observed missing U+2212 in the first page. Final rendered page
contains Chinese/English, minus, Greek/formula symbols, a 155mm vector plot and a table.
This earlier one-page result was subsequently superseded by the end-to-end rehearsal below.
Latest artifacts: `tmp/figure-v2-smoke-03/`; earlier failure/repair evidence stays in
`tmp/figure-v2-smoke-01/` and `tmp/figure-v2-smoke-02/`.
Commands/results: `docs/DESIGN_UPGRADE_V2_REPORT.md`.

The current internal publication chain generated
`output/pdf/CUMCM2026_synthetic_rehearsal.pdf`: 4 A4 pages, 117,964 bytes, SHA256
`59e64d92384815ed1fa81529f13634b2d36c89f3bb508c84fbd3d606ad8f9f3c`.
It contains explicit SYNTHETIC TEST labeling, Chinese prose, a numbered formula, table,
formal figure and caption, second-question text, reference item, appendix and page numbers.
`tests/paper/check_multi_page_pdf.py` confirmed all four A4 pages, required text and Poppler
renders at `tmp/final-pdf-qa/`. The Builder/root inspected the four rendered pages; a separate
read-only `gpt-5.6-terra/high` visual review of frozen SHA
`3c1e04882f7d5e38a94287fe85f89a93085d1232` returned KEEP, P0 none, P1 none, with only a P2
note that the page-3 title/subtitle stack is compact but readable.

One first render attempt was correctly blocked because it ran from the wrong source root;
one bounded cwd retry succeeded. The first PDF checker used an unsuitable pypdf Chinese-text
extraction assertion; the checker was changed to local `pdftotext`, then passed. No package was
installed or upgraded. This verifies the repository's actual synthetic multi-page path, not a
2026 official template, page limit, anonymity rule, AI declaration or real-contest manuscript.

Codex CLI is 0.153.4. Project TOMLs parse. Isolated custom-role runtime probe timed out:
`CONFIGURED_NOT_RUNTIME_VERIFIED`. Native explicitly requested Sol/xhigh returned a design
specification; this does not prove automatic project custom-role discovery or writer isolation.
