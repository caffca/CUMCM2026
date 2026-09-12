# -*- coding: utf-8 -*-
"""write_results：check 件按真实 generator 登记为 diagnostic（满足 IR pair 的 generator 不同 + aggregate 不复用；
primary 仍 authority）。payload/判据/VP 零改动。"""
import io, py_compile
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
a = """    TARGETS = [
        # question, variant, workers, result_file, role, authority
        ("Q1", "full_triple", None, "results/Q1_detect.json", "paper_authority", True),
        ("Q2", "cpsat_lex", 4, "results/Q2_main_w4.json", "model_output", False),  # 诊断性中间件（authority 走 synth）
        ("Q2", "check", None, "results/Q2_check.json", "paper_authority", True),
        ("Q2", "synth", None, "results/Q2_solution.json", "paper_authority", True),
        ("Q3", "bound_elementary", None, "results/Q3_bound.json", "paper_authority", True),
        ("Q3", "check", None, "results/Q3_check.json", "paper_authority", True),
        ("Q3", "synth", None, "results/Q3_solution.json", "paper_authority", True),
        ("Q4", "check", None, "results/Q4_check.json", "paper_authority", True),
        ("Q4", "synth", None, "results/Q4_solution.json", "paper_authority", True),
    ]"""
b = """    TARGETS = [
        # question, variant, workers, result_file, role, authority, generator
        ("Q1", "full_triple", None, "results/Q1_detect.json", "paper_authority", True, "code/prod/q1_solve.py"),
        ("Q2", "cpsat_lex", 4, "results/Q2_main_w4.json", "model_output", False, "code/prod/q2v_cpsat.py"),
        ("Q2", "check", None, "results/Q2_check.json", "model_output", False, "code/prod/check_q2.py"),
        ("Q2", "synth", None, "results/Q2_solution.json", "paper_authority", True, "code/prod/q2_solve.py"),
        ("Q3", "bound_elementary", None, "results/Q3_bound.json", "paper_authority", True, "code/prod/q3_solve.py"),
        ("Q3", "check", None, "results/Q3_check.json", "model_output", False, "code/prod/q3v_check.py"),
        ("Q3", "synth", None, "results/Q3_solution.json", "paper_authority", True, "code/prod/q3_solve.py"),
        ("Q4", "check", None, "results/Q4_check.json", "model_output", False, "code/prod/q4v_check.py"),
        ("Q4", "synth", None, "results/Q4_solution.json", "paper_authority", True, "code/prod/q4_solve.py"),
    ]"""
assert a in s
s = s.replace(a, b)
a2 = """    for q, var, workers, out, role, authority in TARGETS:"""
b2 = """    for q, var, workers, out, role, authority, gen in TARGETS:"""
assert a2 in s
s = s.replace(a2, b2)
a3 = '''               "--generator", "code/prod/q" + q[-1] + "_solve.py",'''
b3 = '''               "--generator", gen,'''
assert a3 in s
s = s.replace(a3, b3)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("write_results: check->diagnostic w/ true generators")
