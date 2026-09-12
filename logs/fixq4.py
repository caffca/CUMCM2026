# -*- coding: utf-8 -*-
import io, json, subprocess, sys, os

p = 'code/prod/q4v_cpsat.py'
s = io.open(p, encoding='utf-8').read()
a = """        for pid, o in hint_acts.items():
            if pid not in plans:
                okp = False
                break"""
b = """        for pid, o in hint_acts.items():
            if pid not in opts:
                okp = False
                planted_reject = "notinopts:" + pid
                break"""
assert a in s, "anchor missing"
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('fixed')

d = 'logs/q4p0re'
os.makedirs(d, exist_ok=True)
cmd = [sys.executable, 'code/prod/q4v_cpsat.py', '--run-id', 'SMOKE-R1', '--parameter',
       json.dumps({'workers': 4, 'stage_budget': {'l1': 20, 'ladder': 10, 'l2': 8, 'l3': 6, 'l4': 6},
                   'q2_solution': '@Q2MAIN', 'anchor': True}),
       '--output-dir', d, '--budget-class', 'full']
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print('rc', r.returncode, (r.stderr or '')[-300:])
pp = json.load(open(os.path.join(d, 'payload.json'), encoding='utf-8'))
print('planted', pp.get('planted_q2_tuple'), 'residual', pp.get('planted_q2_residual'),
      'feasible', pp.get('planted_q2_feasible'), 'own', pp.get('objective_tuple'))
