# Environment

Last updated: 2026-08-24
Status: bootstrap / partially verified

## Supported Environments

| Name | Machine | OS | Python / MATLAB / R | Solver | Environment path | Status |
|---|---|---|---|---|---|---|
| primary | `legend_zyy` local host | Windows 11 家庭中文版, 10.0.22631 / build 22631 / 64-bit | Python 3.12.6 at `C:\Program Files\Python312\python.exe`; MATLAB `NOT_FOUND`; R/Rscript `NOT_FOUND` | Checked `gurobi_cl`, `cplex`, `glpsol`, `cbc`, `highs`, `scip`: all `NOT_FOUND` | system interpreter; `VIRTUAL_ENV` and `CONDA_PREFIX` unset | partially verified |

## Installation / Activation

```bash
# No project activation command has been verified; `VIRTUAL_ENV` and
# `CONDA_PREFIX` were unset during bootstrap.
```

## Verification

```bash
python --version  # verified: Python 3.12.6
python -c "from src.visualization.style import apply_competition_style; apply_competition_style()"
# smoke check: failed because matplotlib is not installed in this interpreter
```

## Key Dependencies

| Package / tool | Version | Purpose | Verified |
|---|---|---|---|
| NumPy | TBD | numerical computing | no |
| Pandas | TBD | tabular data | no |
| SciPy | TBD | statistics / optimization | no |
| Matplotlib | not installed in verified Python interpreter | figures | yes (import failure observed) |
| scikit-learn | TBD | ML / CV | no |
| statsmodels | TBD | statistics / time series | no |
| solver | no checked solver CLI found | optimization | yes (PATH check observed) |

## Safety

- 不修改共享环境，除非明确授权。
- 不自动升级核心依赖。
- 正式结果应记录实际环境与依赖版本。
