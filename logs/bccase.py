# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
def ov(s1, e1, s2, e2):
    return min(e1, e2) - max(s1, s2) > 0
cases = [((165, 170), (170, 175), False), ((165, 170), (167, 172), True),
         ((0, 2), (2, 4), False), ((35, 40), (100, 105), False), ((35, 40), (38, 42), True),
         ((96, 100), (100, 104), False), ((531, 533), (641, 643), False), ((531, 533), (632, 634), True)]
for x, y, z in cases:
    got = ov(x[0], x[1], y[0], y[1])
    if got != z:
        print("MISMATCH", x, y, "expected", z, "got", got)
# 第二实现（大整数位图）同用例
def hit_slots(a, b):
    return any(ov(s1, e1, s2, e2) for s1, e1 in [a] for s2, e2 in [b])
print("check bitmap-style:", ov(531, 533, 641, 643), ov(96, 100, 100, 104))
