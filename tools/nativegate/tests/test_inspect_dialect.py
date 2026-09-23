"""`inspect` speaks dialect: cd too — parity with quickstart/generate.

The cli-reference/fortran-guide contract: a netlib dual-dialect file
answers the same questions through inspect with a flag that generate
already reads from nativegate.yaml. A marked file without the flag must
fail with a message that names the flag, never a raw parser traceback.
"""

import textwrap

from click.testing import CliRunner

from nativegate import cli


DUAL = textwrap.dedent("""\
CS    REAL FUNCTION GAMMA(X)
CD    DOUBLE PRECISION FUNCTION DGAMMA(X)
CS    REAL
CD    DOUBLE PRECISION
     1    C,CONV,EPS
      DGAMMA = 24.0D0
      RETURN
      END
""")


def test_inspect_with_dialect_resolves_and_parses(tmp_path):
    src = tmp_path / "gamma.f"
    src.write_text(DUAL)
    result = CliRunner().invoke(
        cli.main, ["inspect", str(src), "--function", "DGAMMA", "--dialect", "cd"]
    )
    assert result.exit_code == 0, result.output
    assert "function DGAMMA(X: float) -> float" in result.output
    # the rejected CS half stays out of the IR: no standalone GAMMA function
    assert "function GAMMA(" not in result.output


def test_inspect_without_dialect_names_the_flag(tmp_path):
    src = tmp_path / "gamma.f"
    src.write_text(DUAL)
    result = CliRunner().invoke(
        cli.main, ["inspect", str(src), "--function", "DGAMMA"]
    )
    assert result.exit_code != 0
    assert "--dialect cs" in result.output and "--dialect cd" in result.output
    assert "Traceback" not in result.output
