import io
p = 'code/prod/q4v_cpsat.py'
s = io.open(p, encoding='utf-8').read()
a = """    acts = to_actions(final_sel)
    tf = tup(acts)"""
b = """    acts = to_actions(final_sel)
    if not final_sel:
        raise SystemExit("FAIL-CLOSED: Q4 no incumbent (L1 empty)")
    tf = tup(acts)"""
assert a in s
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('q4 fail-closed added')
