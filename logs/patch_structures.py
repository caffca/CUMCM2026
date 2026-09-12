# -*- coding: utf-8 -*-
import io
p = 'code/cs_assemble_brainstorm.py'
s = io.open(p, encoding='utf-8').read()
a1 = '"decision_dimension": 2123, "variable_types": ["binary"], "objective_direction": "maximize",\n  "smoothness": "not_applicable"'
b1 = '"decision_dimension": 2123, "variable_types": ["binary"], "objective_direction": "maximize",\n  "smoothness": "non_smooth"'
a2 = '"decomposability": "partial", "canonical_evaluator_required": True'
b2 = '"decomposability": "no", "canonical_evaluator_required": True'
a3 = '"decision_dimension": 0, "variable_types": ["none"], "objective_direction": "estimate",\n  "smoothness": "not_applicable"'
b3 = '"decision_dimension": 0, "variable_types": ["none"], "objective_direction": "estimate",\n  "smoothness": "non_smooth"'
for a, b in [(a1, b1), (a2, b2), (a3, b3)]:
    assert a in s, a[:50]
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('patched ok')
