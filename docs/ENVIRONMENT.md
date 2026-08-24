# Environment

Last verified: 2026-08-25
Status: **CUMCM core environment READY; attachment compatibility READY; CTeX NOT READY**

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
| CTeX end-to-end compile | NOT READY | MiKTeX could not build `xelatex.fmt`; no changes made |
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

## Verification

- Numerical: NumPy matrix operation, SciPy optimization and SymPy equation solve passed.
- Data: CSV/XLSX write/read with Chinese columns passed.
- Statistics/ML: sklearn linear/logistic regression and statsmodels OLS passed.
- Graph: NetworkX shortest path passed.
- Optimization: CVXPY/CLARABEL, PuLP/CBC and OR-Tools/GLOP small LPs passed.
- Plotting: Matplotlib PNG/PDF export passed.
- Attachment compatibility: xlrd import/version, h5py HDF5 round trip and python-docx Chinese DOCX round trip passed.
- CTeX: minimal Chinese document compile failed during MiKTeX `xelatex.fmt` generation; XeLaTeX executable remains available.
- `python -m pip check`: passed — no broken requirements found.

Test artifacts were removed after the smoke suite. `.venv/` is local and ignored by Git.

## Competition Environment Freeze

The core CUMCM environment is prepared and frozen for normal competition use.

Do not proactively install additional packages during the competition.

New dependencies may be added only when the selected problem requires a capability
that is not reasonably available from the current stack.

## Safety

- Activate only `E:\CUMCM2026\.venv` for this repository.
- No system Python, Conda environment, PATH, CUDA, MATLAB, R, TeX or commercial solver was modified.
- Do not commit `.venv/`, pip cache, smoke files or temporary logs.
