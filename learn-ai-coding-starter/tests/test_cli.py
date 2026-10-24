import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INTERPRETER = ROOT / "sloperator.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTERPRETER), *args], capture_output=True, encoding="utf-8"
    )


def test_runs_a_file():
    completed = run_cli(str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stdout == "hello, slop\n"
    assert completed.stderr == ""


def test_error_goes_to_stderr_after_earlier_output(tmp_path: Path):
    program = tmp_path / "boom.slop"
    program.write_text("hallucinate(“before”)✨\nhallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == "before\n"
    assert completed.stderr == "SlopLang runtime error at line 2: undefined variable 'missing'\n"
    assert "Traceback" not in completed.stderr


def test_missing_file_and_usage():
    assert run_cli().returncode == 2
    missing = run_cli(str(ROOT / "nope.slop"))
    assert missing.returncode == 2
    assert "could not read" in missing.stderr


def test_check_validates_without_running_the_program(tmp_path: Path):
    program = tmp_path / "valid.slop"
    program.write_text("hallucinate(“not executed”)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


@pytest.mark.parametrize(
    ("source", "prefix"),
    [
        ("slop x = 1\n", "SlopLang syntax error"),
        ('hallucinate("straight quotes")✨\n', "SlopLang lexical error"),
    ],
)
def test_check_reports_syntax_and_lexical_errors(tmp_path: Path, source: str, prefix: str):
    program = tmp_path / "broken.slop"
    program.write_text(source, encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr.startswith(prefix)
    assert "Traceback" not in completed.stderr


def test_check_ignores_errors_that_only_happen_at_runtime(tmp_path: Path):
    program = tmp_path / "runtime.slop"
    program.write_text("hallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_flag_may_follow_the_path(tmp_path: Path):
    program = tmp_path / "ok.slop"
    program.write_text("slop x = 1✨\n", encoding="utf-8")
    completed = run_cli(str(program), "--check")
    assert completed.returncode == 0
    assert completed.stdout == ""


def test_check_requires_a_file():
    assert run_cli("--check").returncode == 2
