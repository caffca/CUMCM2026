# -*- coding: utf-8 -*-
import io, subprocess, sys
p = r'code/intake_contracts.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('F.append(fact("F-011", "目标层级",', 'F.append(fact("Q2-F011", "目标层级",')
s = s.replace('''F.append(fact("F-014", "问题1输出", "将结果保存到文件result1.xlsx中（模板文件见附件2），并在论文中给出时频冲突的统计结果", "result1.xlsx+stats", None, "target"))''',
'''F.append(fact("Q1-F014", "问题1输出", "将结果保存到文件result1.xlsx中（模板文件见附件2），并在论文中给出时频冲突的统计结果", "result1.xlsx+stats", None, "target"))''')
s = s.replace('F.append(fact("F-015", "问题2输出"', 'F.append(fact("Q2-F015", "问题2输出"')
s = s.replace('F.append(fact("F-016", "问题2表1格式"', 'F.append(fact("Q2-F016", "问题2表1格式"')
s = s.replace('F.append(fact("F-017", "问题3条件"', 'F.append(fact("Q3-F017", "问题3条件"')
s = s.replace('F.append(fact("F-018", "问题3输出"', 'F.append(fact("Q3-F018", "问题3输出"')
s = s.replace('F.append(fact("F-019", "问题4条件"', 'F.append(fact("Q4-F019", "问题4条件"')
s = s.replace('F.append(fact("F-020", "问题4输出"', 'F.append(fact("Q4-F020", "问题4输出"')
# Q2/Q4 目标层级问题局部登记（同文）
s = s.replace('F.append(fact("F-021", "result2模板列"',
'''F.append(fact("Q4-F011", "目标层级-Q4适用", "应尽可能减少撤销用频计划；尽量减少被调整的用频计划数量；……尽量减少调整的幅度", "lex: revoke_down > adjusted_down > priority > magnitude_down", None, "target", "同 Q2-F011 文本；Q4 目标链与 Q2 一致"))
F.append(fact("F-021", "result2模板列"''')
# 能力 source_fact_ids 同步
s = s.replace('"F-014","F-021"', '"Q1-F014","F-021"').replace('["F-014"]', '["Q1-F014"]')
s = s.replace('["F-015","F-016"]', '["Q2-F015","Q2-F016"]')
s = s.replace('["F-011","F-012"]', '["Q2-F011","F-012"]')
s = s.replace('["F-017"]', '["Q3-F017"]')
s = s.replace('["F-018"]', '["Q3-F018"]')
s = s.replace('["F-019"]', '["Q4-F019"]')
s = s.replace('["F-015"]', '["Q2-F015"]')
s = s.replace('["F-017","F-018"]', '["Q3-F017","Q3-F018"]')
s = s.replace('["F-011","F-019"]', '["Q4-F011","Q4-F019"]')
io.open(p, 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, 'code/intake_contracts.py'], capture_output=True, text=True, encoding='utf-8')
print(r.stdout, r.stderr)
