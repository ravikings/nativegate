"""Fortran parser front door — picks a backend and hides the difference.

Two backends produce the identical `ir.ModuleIR`:

* `fortran_fparser` — a real fparser2 parse tree. The whole file is parsed
  once by a standard-conforming Fortran parser, so routine boundaries,
  declaration attributes, `result(...)` clauses, module nesting and
  continuation lines are read off the tree instead of being reconstructed by
  pattern. This is the parser design.md section 8 ultimately specifies.
* `fortran_regex` — the original line/regex reader, with `fixed_form.py` as
  its fixed-form half. No grammar: each exposed name drives one targeted
  search. Kept as the fallback for machines without fparser, and selectable
  explicitly for reproducing its behaviour.

Selection order, first match wins:

1. the `backend=` argument,
2. `$NATIVEGATE_FORTRAN_PARSER` (`auto` | `fparser2` | `regex`),
3. `parser:` in nativegate.yaml, passed through by the CLI,
4. `auto`.

`auto` resolves to `fparser2` when fparser is importable, and to `regex`
otherwise — the same shape as the C++ side, where Clang is preferred when
available.

WHY THE DEFAULT WAS FLIPPED, AND THE ONE ARGUMENT THAT DECIDED IT

The worry about preferring a real grammar was never that it parses badly. It
was that fparser2 *correctly* refuses invalid Fortran the regex reader
silently accepted, so an existing service built on technically-invalid source
could start failing on upgrade. The parity harness could not answer that: it
only compares files both backends accept.

What answers it is that **nativegate must compile the source with gfortran
anyway** — `f2py -c` shells out to it. So any file gfortran rejects can never
produce a working service, whichever parser read it first. Refusing it at
parse time is then strictly better than mis-binding it and failing later, or
worse, succeeding with wrong intents.

That reduces the question to: does fparser2 refuse anything **gfortran
accepts**? Measured over 180 files — the nine real 1988–1997 fixed-form decks
in `libraries/petro`, plus numpy's own `f2py/tests/src` corpus, which exists
precisely to cover the edge cases f2py must survive — each parsed with
fparser2 and compiled with `gfortran -fsyntax-only`:

    files where fparser2 is STRICTER than gfortran: 0

Every one of the 180 was accepted by both. The three cases that did have to
change during the parity work were *test fixtures*, not library code, and
gfortran rejects all three too (`data declaration statement cannot appear
after executable statements`, `Unclassifiable statement`) — the tests had been
encoding the regex reader's lack of a grammar as a requirement.

The escape hatch stays: `parser: regex` in nativegate.yaml, or
`NATIVEGATE_FORTRAN_PARSER=regex`, pins the old reader. A machine without
fparser installed keeps the regex reader and is unaffected.

Asking for `fparser2` explicitly and not having it is an error, not a silent
downgrade — the same rule the C++ side enforces. A build that quietly loses
symbols because a wheel was missing is exactly the failure this module exists
to prevent.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile

from ..config import ExposeConfig
from ..ir import ModuleIR
from . import fortran_fparser, fortran_regex
from . import hollerith

# Re-exported so callers that reach for the free-form continuation joiner (the
# CLI's source-rewriting paths, and a good number of tests) keep working after
# the implementation moved into fortran_regex.
from .fortran_regex import normalize_free_form  # noqa: F401

BACKENDS = ("auto", "fparser2", "regex")
_ENV_VAR = "NATIVEGATE_FORTRAN_PARSER"

# `auto` -> this, when the backend is actually importable. See the module
# docstring for the evidence behind the flip.
_AUTO_BACKEND = "fparser2"


class ParserUnavailable(RuntimeError):
    """Raised when the requested Fortran backend cannot run on this machine."""


def resolve_backend(backend: str | None = None) -> str:
    """Return "fparser2" or "regex" for a possibly-"auto" request."""
    choice = (backend or os.environ.get(_ENV_VAR) or "auto").lower()
    if choice not in BACKENDS:
        raise ParserUnavailable(
            f"Unknown Fortran parser backend '{choice}'; expected one of {', '.join(BACKENDS)}."
        )

    if choice == "regex":
        return "regex"

    if choice == "fparser2":
        if not fortran_fparser.is_available():
            raise ParserUnavailable(
                "The fparser2 parser was requested but fparser is not usable: "
                f"{fortran_fparser.unavailable_reason()}. Install it with "
                '`pip install "nativegate[fparser]"`, or set parser: regex in '
                "nativegate.yaml."
            )
        return "fparser2"

    if _AUTO_BACKEND == "fparser2" and fortran_fparser.is_available():
        return "fparser2"
    return "regex"


def backend_description(backend: str | None = None) -> str:
    """One line naming the backend in use, for `ngate inspect`/`generate`."""
    try:
        resolved = resolve_backend(backend)
    except ParserUnavailable as exc:
        return str(exc)
    requested = (backend or os.environ.get(_ENV_VAR) or "").lower()
    if resolved == "fparser2":
        version = fortran_fparser.fparser_version()
        if requested == "fparser2":
            return f"fparser2 parse tree ({version}, selected explicitly)"
        return f"fparser2 parse tree ({version}, default)"
    if requested == "regex":
        return "regex reader (selected explicitly)"
    # The only other way to land on regex is `auto` with no fparser installed.
    # Say so plainly: this is a real capability difference, not a preference,
    # and someone reading a build log should be able to tell which they got.
    return (
        "regex reader (no grammar; fparser unavailable: "
        f"{fortran_fparser.unavailable_reason()}. Install with "
        '`pip install "nativegate[fparser]"` for the parse-tree backend)'
    )


def _hollerith_resolved(path: Path) -> Path | None:
    """A temp copy of `path` with Hollerith constants resolved, or None.

    fparser2 refuses Hollerith constants gfortran compiles with a warning —
    the one measured counterexample to the parity rule that made fparser2
    the default (DEFECTS D15, netlib quadpack). The file gfortran accepts
    is the file that should parse, so the front door resolves the constants
    into their standard quoted spelling and reads that copy instead. The
    copy is attributed back to the original path, so source-file references
    and doc-comment line spans keep pointing at the real file.
    """
    raw = path.read_text()
    if not hollerith.is_hollerith(raw):
        return None
    resolved, _ = hollerith.resolve_hollerith(raw)
    handle, name = tempfile.mkstemp(suffix=path.suffix)
    Path(name).write_text(resolved)
    # mkstemp exposes an int fd; close it — Path.write_text already used
    # a second open, and the raw descriptor must not leak.
    import os

    os.close(handle)
    return Path(name)


def parse_source(
    path: Path,
    expose: ExposeConfig,
    include_paths: list[Path] | None = None,
    *,
    backend: str | None = None,
) -> ModuleIR:
    """Parse one Fortran source into a ModuleIR using the selected backend."""
    if resolve_backend(backend) == "fparser2":
        resolved = _hollerith_resolved(path)
        if resolved is not None:
            module = fortran_fparser.parse_source(resolved, expose, include_paths)
            # The temp copy must not leak into user-visible IR: same name,
            # same source file, only the text differs (D15).
            module.name = path.stem
            module.source_file = str(path)
            resolved.unlink(missing_ok=True)
            return module
        return fortran_fparser.parse_source(path, expose, include_paths)
    return fortran_regex.parse_source(path, expose, include_paths)


def list_routine_names(path: Path, *, backend: str | None = None) -> list[str]:
    """Every function/subroutine name in the file, in source order."""
    if resolve_backend(backend) == "fparser2":
        resolved = _hollerith_resolved(path)
        if resolved is not None:
            try:
                return fortran_fparser.list_routine_names(resolved)
            finally:
                resolved.unlink(missing_ok=True)
        return fortran_fparser.list_routine_names(path)
    return fortran_regex.list_routine_names(path)
