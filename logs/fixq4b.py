import io
p = 'code/prod/q4v_cpsat.py'
s = io.open(p, encoding='utf-8').read()
a = '"planted_reject_reason": planted if None else None,'
if a in s:
    s = s.replace(a, '"planted_reject_reason": planted_reject,')
    io.open(p, 'w', encoding='utf-8').write(s)
    print('reject field fixed')
else:
    print('pattern not found; present lines:')
    for ln in s.splitlines():
        if 'planted_reject' in ln:
            print('  ', ln.strip()[:120])
