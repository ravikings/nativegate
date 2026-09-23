"""D9 regression: dash-named services are rejected at scaffold time, not
at generate time with invalid generated Python.

First contact with netlib specfun (2026-09-23): `ngate quickstart gamma.f
--name specfun-gamma` scaffolded cleanly, generated
`from ._native.specfun-gamma import ...` — invalid syntax — and only
nativegate's generated-file compile() gate refused to write it, three
commands after the moment the user should have been told.
"""

import pytest
from click.testing import CliRunner

from nativegate import cli


@pytest.fixture()
def scratch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("bad", ["specfun-gamma", "2lib", "class"])
def test_create_service_rejects_non_identifier_names(scratch, bad):
    result = CliRunner().invoke(cli.main, ["create-service", bad, "--language", "fortran"])
    assert result.exit_code != 0
    assert "Python package" in result.output
    # nothing may have been written
    assert not (scratch / "services").exists()


def test_quickstart_rejects_dash_named_service_and_explains(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "gamma.f"
    source.write_text("      DOUBLE PRECISION FUNCTION DGAMMA(X)\n      END\n")
    result = CliRunner().invoke(
        cli.main, ["quickstart", str(source), "--name", "specfun-gamma"]
    )
    assert result.exit_code != 0
    assert "--name specfun_gamma" not in result.output


def test_valid_underscored_name_still_scaffolds(scratch):
    result = CliRunner().invoke(
        cli.main, ["create-service", "specfun_gamma", "--language", "fortran"]
    )
    assert result.exit_code == 0, result.output
