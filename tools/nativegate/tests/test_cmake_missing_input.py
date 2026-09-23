"""D11: a service tree consumed without `generate` must say so at configure
time.

The generated CMake references native/_expanded/ sources that `ngate
generate` writes. A packaging commit that ships the service tree without
them (the exact failure of specfun-py's first CI run) surfaced as ninja's
"no known rule to make it" mid-build, with the remedy buried one exception
down a log. The generated CMake now fatals at configure time with the
remedy written out.
"""

import shutil
import textwrap
from pathlib import Path

import pytest

from nativegate.generators import f2py_gen


def test_generated_cmake_carries_the_missing_input_guard():
    cmake = f2py_gen.generate_cmake(
        type("M", (), {"name": "specfun"})(),
        "specfun",
        ["native/_expanded/gamma.f"],
    )
    assert "foreach(f2py_source IN LISTS F2PY_SOURCES)" in cmake
    assert "NOT EXISTS" in cmake
    assert "ngate generate" in cmake


@pytest.mark.skipif(shutil.which("cmake") is None, reason="cmake not on PATH")
@pytest.mark.skipif(
    shutil.which("gfortran") is None, reason="Fortran language check needs a compiler"
)
def test_guard_fires_when_the_input_file_is_absent(tmp_path):
    cmake = f2py_gen.generate_cmake(
        type("M", (), {"name": "specfun"})(),
        "specfun",
        ["native/_expanded/gamma.f"],
    )
    (tmp_path / "CMakeLists.txt").write_text(cmake)
    (tmp_path / "native" / "_expanded").mkdir(parents=True)
    (tmp_path / "native" / "_expanded" / "gamma.f").write_text(
        textwrap.dedent("""\
            MISSING
            """)
    )
    (tmp_path / "native" / "_expanded" / "gamma.f").unlink()

    result = _configure(tmp_path)
    combined = result.stdout + result.stderr
    assert "Missing build input" in combined
    assert "ngate generate specfun" in combined
    # and NOT the misleading ninja symptom
    assert "no known rule to make it" not in combined


def _configure(tmp_path):
    import subprocess
    import sys
    env_path = sys.executable
    return subprocess.run(
        ["cmake", "-S", str(tmp_path), "-B", str(tmp_path / "build"),
         f"-DPython_EXECUTABLE={env_path}"],
        capture_output=True, text=True,
    )
