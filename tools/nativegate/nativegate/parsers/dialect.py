"""Dialect selection for netlib-style dual-dialect Fortran (DEFECTS D10).

Some netlib-era sources (specfun 2.5 is the canonical case, 1996) mark
machine precision by commenting EVERY statement in both dialects and
asking the installer to comment one batch out manually:

    CS    REAL FUNCTION GAMMA(X)
    CD    DOUBLE PRECISION FUNCTION DGAMMA(X)
    CS    REAL
    CD    DOUBLE PRECISION
         1    C,CONV,EPS, ...            <- no statement starts in column 7

With neither prefix commented, no standard parser can read the file: the
grammar has a floating continuation with no statement behind it, and
gfortran rejects it too ("no implicit type at 'CS'..." paired with the
dangling continuation). The `NATIVEGATE_FORTRAN_PARSER=regex` fallback
does not help — the FUNCTION statements are marked the same way.

`apply_dialect` makes the choice static in place: the selected prefix is
uncommented (its two characters become blank columns) and the other
prefix is pushed under a comment (`C` + whatever remained). Column
positions are preserved, which is what fixed-form requires: `CS   1 `
(col 3-6 blank, 1 in column 6) and `CD` lines follow the same geometry.

Idempotent: after one pass no line starts CS/CD any more, so re-running
on an already-resolved file is a no-op, which is what makes it safe for
generate to apply it to every source without knowing which ones are
marked.

The transform is deliberately pure text on the fixed-form column grid:
uncommenting replaces the two marker characters with two blanks, so no
column ever shifts, and commenting restores the `C` in column 1. Only
`native/_expanded/` carries the resolved file — the byte-for-byte copy
under `native/native/...` is untouched, so provenance (`golden.json`
hashes) keeps describing the upstream source, not the transform output.
"""

from __future__ import annotations

import re

DIALECT_CHOICES = ("cs", "cd")

_PREFIX_RE = re.compile(r"^(CS|CD)(?=[ \t])", re.IGNORECASE | re.MULTILINE)


def resolve_dialect(raw: str | None) -> str:
    """Validate a `dialect:` value from nativegate.yaml / --dialect.

    `""` means "the source is not dialect-marked, leave everything alone".
    Anything unlisted is an error, not a silent no-op — a typo'd
    `dialect: dc` must fail here, not turn into "unresolved source".
    """
    value = (raw or "").strip().lower()
    if value and value not in DIALECT_CHOICES:
        raise ValueError(
            f"Unknown dialect '{value}'; expected one of: "
            + ", ".join(DIALECT_CHOICES) + " (or empty for none)."
        )
    return value.lower()


def is_dialect_marked(text: str) -> bool:
    """True when any expected prefix appears at a statement column.

    Deliberately coarse: a file with the markers gets resolved from the
    start, whether or not every line carries them. A single CS/CD word
    that opens a line is a genuine dialect marker in practice — no Fortran
    statement begins with those letters in column 1.
    """
    return bool(_PREFIX_RE.search(text))


def apply_dialect(text: str, dialect: str) -> str:
    """Resolve the dual-dialect marking to a single live dialect.

    `dialect` is the prefix that becomes the code; the other becomes a
    comment (`C ` + the remainder), so the rejected variant stays readable
    in place — the same shape the files will have after a human editor
    does the step netlib's readme prescribes.
    """
    dialect = resolve_dialect(dialect)
    if not dialect or not is_dialect_marked(text):
        return text

    selected = dialect.upper()
    out = []
    for line in text.splitlines(keepends=True):
        match = _PREFIX_RE.match(line)
        if not match:
            out.append(line)
            continue
        marker = match.group(1).upper()
        if marker == selected:
            out.append("  " + line[2:])
        else:
            out.append("C " + line[2:])
    return "".join(out)
