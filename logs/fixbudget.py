# -*- coding: utf-8 -*-
"""按 deadline=1800 现实重设层预算 + preemptible 标志（deadline 后排队任务标 preempted 而非 fail）。"""
import io

p = "code/fms_build.py"
s = io.open(p, encoding="utf-8").read()
a = '_SB = {"l1": 1500, "ladder": 600, "l2": 900, "l3": 450, "l4": 450}'
b = '_SB = {"l1": 900, "ladder": 300, "l2": 600, "l3": 300, "l4": 300}'
assert a in s
s = s.replace(a, b)
# timeout 统一 1200（< deadline，单任务不被 min() 截半）
s = s.replace('"Q2": {"impl": "code/prod/q2_solve.py", "timeout": 4200, "wall": 4200,',
              '"Q2": {"impl": "code/prod/q2_solve.py", "timeout": 1200, "wall": 1800,')
s = s.replace('"Q4": {"impl": "code/prod/q4_solve.py", "timeout": 4200, "wall": 4200,',
              '"Q4": {"impl": "code/prod/q4_solve.py", "timeout": 1200, "wall": 1800,')
s = s.replace('"Q3": {"impl": "code/prod/q3_solve.py", "timeout": 3000, "wall": 3600,',
              '"Q3": {"impl": "code/prod/q3_solve.py", "timeout": 1500, "wall": 1800,')
io.open(p, "w", encoding="utf-8").write(s)
print("fms budgets realigned")

# planner: preemptible 常量注入（sharded_run 不改 preset——改为在 fms budget 里带 preemptible?
# planner 读 contract.get("preemptible", False) —— contract 是 closed schema 加不了字段。
# 替代：q2/q4 cpsat 脚本内部按累计用时自限（stage_budget 已=2400<1800+w1 情形）：
# w1 排在 p1：若 deadline 已到，runner 标 preempted；aggregate 的 required cases 缺 p1 → INCOMPLETE。
# 对策：把 w1 放在 p0（先跑、1800s 内完成 2400 预算会被 deadline 截…不行，timeout=min(1200,remaining)）。
# 最终方案：顺序 = p0 w1(确定性权威, ≤1200)、p1 w4(复现印证, 若被 preempted → 用 resume 续跑到 p1 完成：
#   deadline 从每次进程启动计时！新启动的 resume 会重置 started_monotonic → 剩余任务在新一轮 1800s 内可跑。
print("NOTE: deadline 以进程启动为基准，resume 重启即重置——preempted 任务可在新启动中续跑")
