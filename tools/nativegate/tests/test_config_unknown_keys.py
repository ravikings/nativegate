"""Unknown top-level keys in nativegate.yaml must fail loading.

Found in the wild (2026-09-23): specfun-py's CI installed a nativegate
that pre-dated the `dialect:` key and generated the service anyway from
an assumption never written down — the unknown key was swallowed as dead
weight. A typo in any key was equally silent. Now both are config errors
that say what is wrong and what to do about it.
"""

import shutil
import textwrap

import pytest

from nativegate.config import ConfigError, ServiceConfig


@pytest.fixture()
def scratch(tmp_path, monkeypatch):
    service = tmp_path / "demo"
    (service / "native").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return service


def _config_for_lines(text):
    def _load(service):
        (service / "nativegate.yaml").write_text(text)
        return ServiceConfig.load(service)
    return _load


def test_unknown_key_is_an_error(scratch):
    (scratch / "nativegate.yaml").write_text(textwrap.dedent("""\
        name: demo
        language: fortran
        diatect: cd
        expose:
          functions: []
        """))
    with pytest.raises(ConfigError) as exc:
        ServiceConfig.load(scratch)
    assert "diatect" in str(exc.value)
    assert "upgrade nativegate" in str(exc.value)


def test_future_key_is_a_config_error_not_a_silent_noop(scratch):
    (scratch / "nativegate.yaml").write_text(textwrap.dedent("""\
        name: demo
        language: fortran
        dialect: cd
        expose:
          functions: []
        """))
    # fine on a nativegate that knows the key
    config = ServiceConfig.load(scratch)
    assert config.dialect == "cd"


def test_all_declared_keys_still_load(scratch):
    (scratch / "nativegate.yaml").write_text(textwrap.dedent("""\
        name: demo
        language: fortran
        dialect: cd
        parser: auto
        libraries:
        - petro
        include_paths: []
        fortran:
          defines: []
        expose:
          all: true
        """))
    config = ServiceConfig.load(scratch)
    assert config.dialect == "cd"
    assert config.libraries == ["petro"]
    assert config.expose.all is True
