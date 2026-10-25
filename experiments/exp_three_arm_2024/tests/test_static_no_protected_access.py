"""Static guard: no package code may load a protected 2025 file or import the 2025 campaign modules.
- scripts/: banned strings are searched in executable code only (comments and docstrings removed), since
  provenance docstrings legitimately cite the old runner by file:line.
- tests/: no import of a banned module (AST check). Test files may list banned strings as guard data.
Reads only this package's own .py files."""
import ast
import io
import tokenize
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
BANNED_STRINGS = ("2025.csv", "DECOMPOSITION_2025", "WEATHER_2025", "planner_cf_campaign_runner",
                  "planner_cf_hash_guards", "stage4_planner_cf_consistency_2025/CAMPAIGN",
                  "EBR_PER_ORIGIN_OUTCOME_LABELS", "EBR_DECISION_TIME_FEATURES_PER_ORIGIN",
                  "research_ebr_population_diagnostic")
BANNED_MODULES = ("planner_cf_campaign_runner", "planner_cf_hash_guards")
SCRIPTS = sorted((PKG / "scripts").glob("*.py"))
TESTS = sorted((PKG / "tests").glob("*.py"))


def _code_only(src: str) -> str:
    tree = ast.parse(src)
    doc_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) \
                    and isinstance(node.body[0].value.value, str):
                d = node.body[0]
                doc_lines.update(range(d.lineno, d.end_lineno + 1))
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT or tok.start[0] in doc_lines:
            continue
        out.append(tok.string)
    return " ".join(out)


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_scripts_have_no_banned_reference(path):
    code = _code_only(path.read_text())
    for b in BANNED_STRINGS:
        assert b not in code, f"{path.name} references {b} in executable code"


@pytest.mark.parametrize("path", SCRIPTS + TESTS, ids=lambda p: p.name)
def test_no_banned_imports(path):
    for node in ast.walk(ast.parse(path.read_text())):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""] + [a.name for a in node.names]
        for n in names:
            for b in BANNED_MODULES:
                assert b not in n, f"{path.name} imports {n}"


def test_scripts_compile():
    for p in SCRIPTS:
        compile(p.read_text(), str(p), "exec")
