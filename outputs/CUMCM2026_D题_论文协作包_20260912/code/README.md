# 协作包代码说明

`code/` 是当前仓库 `scripts/`、`src/d_problem/` 和 `tests/d_problem/` 的可复现副本。
下面的命令应在压缩包解压后的根目录执行，并显式指定 `data/`、`results/` 路径；不要
直接依赖原仓库脚本中的默认路径。

```text
python code/scripts/solve_d_q1.py --input data/附件1.xlsx --template data/附件2/result1.xlsx --output results/q1/result1_reproduced.xlsx
python code/scripts/solve_d_q3.py --input data/附件1.xlsx --template data/附件2/result3.xlsx --q2-selected results/q2/Q2-T-incumbent-v1.json --output results/q3/result3_reproduced.xlsx
python code/scripts/validate_d_q4_result.py --input data/附件1.xlsx --workbook results/q4/result4.xlsx --selected results/q4/selected_T.json --output results/q4/result4_readback_check_reproduced.json
```

Q2/Q4 完整求解需要 OR-Tools 等依赖；仅阅读本包中的 Markdown、JSON 和 Excel 不需要
重新安装求解器。测试脚本的默认附件路径面向原仓库，若在压缩包中运行请按同样原则
显式改写路径或把 `data/` 映射为项目附件目录；本包已将测试中的附件路径适配为
包根目录下的 `data/附件1.xlsx`，因此 `python -m unittest discover -s code/tests/d_problem`
可直接运行。
