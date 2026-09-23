"""D14: `external` dummies are callbacks — refusing to type them.

First contact: netlib quadpack QAGSE (f2py itself refuses — 'external f
is not in lcb_map[]'). The regex reader's IMPLICIT fallback typed 'f' as
`real` -> float: a binding that builds, imports, passes its smoke test
and hands the Fortran side garbage at call time. Both backends now
refuse the routine as a whole with the reason; ModuleIR.skipped carries
it. NOTE: the synthetic decks are written with hard six-space margins —
textwrap.dedent strips the shared indent and the files stop being
fixed-form.
"""

from pathlib import Path

from nativegate.config import ExposeConfig
from nativegate.parsers import fortran as fortran_parser

HEADER_SUB = (
    "      SUBROUTINE QNG(F, A, B)\n"
    "      EXTERNAL F\n"
    "      REAL A, B\n"
    "      END\n"
)

HEADER_FREE = (
    "subroutine qng(f, a, b)\n"
    "  external f\n"
    "  real a, b\n"
    "end subroutine qng\n"
)

HEADER_PLAIN = (
    "      SUBROUTINE ASSOC(A, B)\n"
    "      REAL A, B\n"
    "      A = B\n"
    "      RETURN\n"
    "      END\n"
)


def test_regex_backend_reports_external_dummy_as_skip(tmp_path):
    src = tmp_path / "qng.f"
    src.write_text(HEADER_SUB)
    module = fortran_parser.parse_source(
        src, ExposeConfig(functions=["QNG"]), backend="regex"
    )
    assert module.functions == []
    assert len(module.skipped) == 1
    assert module.skipped[0].name == "QNG"
    assert "EXTERNAL" in module.skipped[0].reason


def test_fparser_backend_reports_external_dummy_as_skip(tmp_path):
    src = tmp_path / "qng.f"
    src.write_text(HEADER_SUB)
    module = fortran_parser.parse_source(
        src, ExposeConfig(functions=["QNG"]), backend="fparser2"
    )
    assert module.functions == []
    assert "EXTERNAL" in module.skipped[0].reason


def test_free_form_backend_also_refuses_callbacks(tmp_path):
    src = tmp_path / "qng.f90"
    src.write_text(HEADER_FREE)
    module = fortran_parser.parse_source(
        src, ExposeConfig(functions=["qng"]), backend="regex"
    )
    assert module.functions == []
    assert len(module.skipped) == 1


def test_routines_without_callbacks_still_bind(tmp_path):
    src = tmp_path / "g.f"
    src.write_text(HEADER_PLAIN)
    module = fortran_parser.parse_source(
        src, ExposeConfig(functions=["ASSOC"]), backend="regex"
    )
    assert [p.name.lower() for p in module.functions[0].parameters] == ["a", "b"]
