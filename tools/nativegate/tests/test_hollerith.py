"""D15: Hollerith constants resolve so fparser2 reads gfortran-acceptable files.

`call xerror(26habnormal return from  qng ,26,ier,0)` compiles under
gfortran with a legacy-extension warning but made fparser2 refuse the
whole file — QUADPACK's QNG, un-inspectable at the default backend. The
front door now resolves these into the standard quoted spelling in a temp
copy attributed back to the original path (same module name, same source
file reference, same line count), so both `inspect` and `generate` see
the file the compiler sees.
"""

import textwrap
from pathlib import Path

from click.testing import CliRunner

from nativegate import cli
from nativegate.parsers import fortran as fortran_parser
from nativegate.parsers import hollerith
from nativegate.config import ExposeConfig

QNG_WITH_HOLLERITH = (
    "      SUBROUTINE QNG(F, A, B)\n"
    "      EXTERNAL F\n"
    "      REAL A, B\n"
    "         IF (IER.NE.0) THEN\n"
    "   80 CALL XERROR(26HABNORMAL RETURN FROM  QNG ,26,IER,0)\n"
    "         END IF\n"
    "      RETURN\n"
    "      END\n"
)


def test_resolver_quotes_and_preserves_columns():
    source = QNG_WITH_HOLLERITH
    out, resolved = hollerith.resolve_hollerith(source)
    assert resolved == 1
    assert "26HABNORMAL" not in out
    assert "'ABNORMAL RETURN FROM  QNG '" in out
    # line count and margin are invariants: every physical line stays
    assert out.count("\n") == source.count("\n")
    for original, rewritten in zip(source.splitlines(), out.splitlines()):
        assert len(rewritten) <= 72


def test_resolver_leaves_continuation_spanning_constants():
    # the constant counts past the physical line: untouched, so line
    # numbers never shift
    text = "      CALL XERROR(6HABCDE\n      -F,6,IER,0)\n"
    out, resolved = hollerith.resolve_hollerith(text)
    assert resolved == 0
    assert out == text


def test_resolver_is_a_noop_without_hollerith():
    text = "      REAL A\n      A = 2.0\n"
    out, resolved = hollerith.resolve_hollerith(text)
    assert resolved == 0 and out == text


def test_quote_escapes_are_balanced():
    assert hollerith._quote("it's") == '"it\'s"'
    assert hollerith._quote('say "hi"') == '\'say "hi"\''


def test_inspect_parses_hollerith_deck_by_default(tmp_path):
    src = tmp_path / "qng.f"
    src.write_text(QNG_WITH_HOLLERITH)
    # the ONE check that matters: no explicit backend flag, the default
    # (fparser2 where importable) reads the file the compiler reads
    result = CliRunner().invoke(
        cli.main, ["inspect", str(src), "--function", "QNG"]
    )
    assert result.exit_code == 0, result.output
    # the callback is refused with its reason, never mis-typed (D14)
    assert "EXTERNAL" in result.output


def test_module_name_attributed_to_real_file(tmp_path):
    src = tmp_path / "qng.f"
    src.write_text(QNG_WITH_HOLLERITH)
    module = fortran_parser.parse_source(src, ExposeConfig(functions=["QNG"]))
    assert module.name == "qng"
    assert module.source_file == str(src)
