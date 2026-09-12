# -*- coding: utf-8 -*-
import io
p = 'code/cs_assemble_brainstorm.py'
s = io.open(p, encoding='utf-8').read()
assert '"decomposability": "partial"' in s
s = s.replace('"decomposability": "partial"', '"decomposability": "no"')
print('smoothness left:', s.count('"smoothness": "not_applicable"'))
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
