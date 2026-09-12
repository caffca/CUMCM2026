# -*- coding: utf-8 -*-
import io
p = 'code/fms_build.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('cc("analytical_verifier", "code/q1_detect.py + code/q1_verify.py",',
              'cc("analytical_verifier", "code/prod/q1_solve.py",')
s = s.replace('"三实现两两对称差=0；独立第二实现 checker；半开边界用例"),',
              '"三实现两两对称差=0；独立第二实现 checker；半开边界用例", qid="Q1"),')
io.open(p, 'w', encoding='utf-8').write(s)
assert 'qid="Q1"' in s and 'code/prod/q1_solve.py' in s
print('fms_build patched ok')
