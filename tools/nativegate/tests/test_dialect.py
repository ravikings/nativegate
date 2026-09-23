"""D10: the netlib CS/CD dual-dialect marking.

Sources fetched straight from netlib specfun carry every statement twice,
in both dialects, comment-marked by prefix (CS = single, CD = double), and
the installer comments one batch out by hand. Neither parser could read
such a file — the fixed-form grammar sees a continuation with no statement,
and the regex fallback finds no routine because the FUNCTION lines are
marked too. The fix is `dialect:` in nativegate.yaml / `--dialect` on
quickstart: the chosen prefix's lines become the code, the other prefix's
lines become comments, and the resolved copy lives under native/_expanded
so the untouched upstream bytes stay in native/.
"""

import textwrap

import pytest
from click.testing import CliRunner

from nativegate import cli
from nativegate.parsers.dialect import (
    apply_dialect,
    is_dialect_marked,
    resolve_dialect,
)


# --- unit ----------------------------------------------------------------


def test_resolve_dialect_validates():
    assert resolve_dialect("") == ""
    assert resolve_dialect("CS") == "cs"
    assert resolve_dialect("cd") == "cd"
    with pytest.raises(ValueError):
        resolve_dialect("dc")     # plausible typo must fail, not act as a no-op
    with pytest.raises(ValueError):
        resolve_dialect("both")


DUAL_DIALECT = textwrap.dedent("""\
CS    REAL FUNCTION GAMMA(X)
CD    DOUBLE PRECISION FUNCTION DGAMMA(X)
CS    REAL
CD    DOUBLE PRECISION
     1    C,CONV,EPS
      DGAMMA = 24.0D0
      RETURN
      END
""")


def test_apply_dialect_selects_cd():
    out = apply_dialect(DUAL_DIALECT, "cd")
    lines = out.splitlines()
    # the chosen CD lines are live, shifted two columns into statement
    # position, with no other column moved
    assert "      DOUBLE PRECISION FUNCTION DGAMMA(X)" in lines
    assert "      DOUBLE PRECISION" in lines
    # the rejected CS half is commented back to the normal fixed-form
    # comment form, `C` in column 1
    assert "C     REAL FUNCTION GAMMA(X)" in lines
    assert "C     REAL" in lines
    # untouched lines are untouched
    assert "      DGAMMA = 24.0D0" in lines
    assert "     1    C,CONV,EPS" in lines


def test_apply_dialect_selects_cs():
    out = apply_dialect(DUAL_DIALECT, "cs")
    lines = out.splitlines()
    assert "      REAL FUNCTION GAMMA(X)" in lines
    assert "      REAL" in lines
    commented = [line for line in lines if line.startswith("C ")]
    assert any("DGAMMA" in line and "DOUBLE PRECISION FUNCTION" in line
               for line in commented)


def test_apply_dialect_leaves_plain_source_alone():
    plain = "      DOUBLE PRECISION FUNCTION DGAMMA(X)\n      END\n"
    assert apply_dialect(plain, "cd") == plain
    assert apply_dialect(plain, "") == plain


def test_apply_dialect_is_idempotent():
    once = apply_dialect(DUAL_DIALECT, "cd")
    assert apply_dialect(once, "cd") == once
    assert not is_dialect_marked(once)


def test_is_dialect_marked():
    assert is_dialect_marked(DUAL_DIALECT)
    assert not is_dialect_marked(apply_dialect(DUAL_DIALECT, "cd"))
    assert not is_dialect_marked("")


def test_apply_dialect_rejects_bad_dialect():
    with pytest.raises(ValueError):
        apply_dialect(DUAL_DIALECT, "dc")


# --- config round-trip -----------------------------------------------------


def test_config_round_trips_dialect(tmp_path):
    """`dialect:` survives a save/load cycle, and an unknown value is a
    config error rather than a silently ignored key."""
    import yaml
    from nativegate.config import ServiceConfig

    service = tmp_path / "specfun_gamma"
    service.mkdir(parents=True)
    (service / "nativegate.yaml").write_text(
        yaml.dump({"name": "specfun_gamma", "language": "fortran",
                   "dialect": "cd", "expose": {"functions": []}},
                  sort_keys=False),
    )
    config = ServiceConfig.load(service)
    assert config.dialect == "cd"

    config.save(service)
    reloaded = ServiceConfig.load(service)
    assert reloaded.dialect == "cd"

    (service / "nativegate.yaml").write_text(
        yaml.dump({"name": "specfun_gamma", "language": "fortran",
                   "dialect": "dc", "expose": {}},
                  sort_keys=False),
    )
    with pytest.raises(Exception, match="dialect"):
        ServiceConfig.load(service)


# --- CLI wiring -----------------------------------------------------------


@pytest.fixture()
def netlib_scratch(tmp_path, monkeypatch):
    source = tmp_path / "gamma.f"
    source.write_text(DUAL_DIALECT)
    monkeypatch.chdir(tmp_path)
    return source


def test_quickstart_dialect_generates_and_keeps_native_untouched(netlib_scratch, tmp_path):
    result = CliRunner().invoke(
        cli.main,
        ["quickstart", str(netlib_scratch), "--name", "specfun_gamma",
         "--dialect", "cd"],
    )
    assert result.exit_code == 0, result.output

    service = tmp_path / "services" / "specfun_gamma"
    native = service / "native" / "gamma.f"
    assert native.read_text() == DUAL_DIALECT
    resolved = service / "native" / "_expanded" / "gamma.f"
    assert resolved.exists()
    assert resolved.read_text().rstrip("\n") == apply_dialect(
        DUAL_DIALECT, "cd"
    ).rstrip("\n")

    assert "dialect: cd" in (service / "nativegate.yaml").read_text()

    init = service / "python" / "specfun_gamma" / "__init__.py"
    assert "dgamma" in init.read_text().lower()


def test_without_dialect_the_marked_file_fails_with_a_direction(netlib_scratch):
    result = CliRunner().invoke(
        cli.main, ["quickstart", str(netlib_scratch), "--name", "specfun_gamma"]
    )
    assert result.exit_code != 0
    # the parser error is passed through, but the remedy is named
    assert "dialect-marked" in result.output
    assert "--dialect cs" in result.output and "--dialect cd" in result.output


def test_bad_dialect_is_an_error_not_a_noop(netlib_scratch):
    result = CliRunner().invoke(
        cli.main,
        ["quickstart", str(netlib_scratch), "--name", "specfun_gamma",
         "--dialect", "dc"],
    )
    assert result.exit_code != 0
    assert "Unknown dialect" in result.output
