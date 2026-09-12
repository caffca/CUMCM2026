# -*- coding: utf-8 -*-
"""按 deadline=1800 重设层预算（单次 cpsat≤1500）+ 重写波次（长任务独占波）。"""
import io

p = "code/fms_build.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('_SB = {"l1": 1500, "ladder": 600, "l2": 900, "l3": 450, "l4": 450}',
              '_SB = {"l1": 800, "ladder": 250, "l2": 300, "l3": 100, "l4": 50}')
s = s.replace('"Q2": {"impl": "code/prod/q2_solve.py", "timeout": 4200, "wall": 4200,',
              '"Q2": {"impl": "code/prod/q2_solve.py", "timeout": 1700, "wall": 1700,')
s = s.replace('"Q4": {"impl": "code/prod/q4_solve.py", "timeout": 4200, "wall": 4200,',
              '"Q4": {"impl": "code/prod/q4_solve.py", "timeout": 1700, "wall": 1700,')
s = s.replace('"Q3": {"impl": "code/prod/q3_solve.py", "timeout": 3000, "wall": 3600,',
              '"Q3": {"impl": "code/prod/q3_solve.py", "timeout": 1500, "wall": 1500,')
s = s.replace('"limit": 1200}', '"limit": 600}').replace('"limit": 900}', '"limit": 600}')
io.open(p, "w", encoding="utf-8").write(s)
print("fms budgets fit deadline(1800): l1=800 ladder=250 l2=300 l3=100 l4=50 =1500s")
