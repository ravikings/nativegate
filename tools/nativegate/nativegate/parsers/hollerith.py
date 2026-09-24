"""Hollerith constants in fixed-form Fortran — rewrite to CHARACTER literals.

The netlib quadpack contact (DEFECTS D15) is the canonical case: 1970s-era
sources pass error text as Hollerith constants,

    call xerror(26habnormal return from  qng ,26,ier,0)

gfortran compiles that (legacy extension, warning only), but fparser2
refuses the whole file — the first measured counterexample to the
"fparser2 is never stricter than gfortran" rule that justifies fparser2
being the default front end. Since nativegate must compile with gfortran
anyway, the file gfortran accepts is exactly the file that should reach
the parser; the quoted CHARACTER constant is the standard F77 spelling of
the same argument, which f2py's own reader accepts too.

Deliberately conservative:

* Fixed-form text only; F90+ sources do not carry Hollerith.
* One constant per physical line: an `N*H` whose count runs past the line
  end (it continues onto the next) is left untouched — rewriting it would
  move every following line number and shift the doc-comment spans both
  backends position by line.
* The rewritten line must fit the punch-card margin (72 columns). One
  that cannot is left alone. What survives un-resolved is the caller's
  decision (see resolver_hollerith in parsers/fortran.py).
"""

from __future__ import annotations

import re

_HOLLERITH_START_RE = re.compile(r"(?<!\w)(\d+)\s*[hH]", re.ASCII)

_FIXED_FORM_LINE_LIMIT = 72


def is_hollerith(text: str) -> bool:
    return bool(_HOLLERITH_START_RE.search(text))


def resolve_hollerith(text: str) -> tuple[str, int]:
    """Replace resolvable Hollerith constants with quoted literals, in line.

    Returns (text, resolved). Line count is always preserved, so line-based
    spans (doc comments, fparser2 item spans) stay put — the same invariant
    the dialect pass keeps.
    """
    if not is_hollerith(text):
        return text, 0

    out_lines = []
    resolved_total = 0
    for line in text.splitlines(keepends=True):
        resolved_line, n = _resolve_line(line)
        out_lines.append(resolved_line)
        resolved_total += n
    return "".join(out_lines), resolved_total


def _resolve_line(line: str) -> tuple[str, int]:
    """Substitute every fitting Hollerith constant on one physical line."""
    end_of_line = len(line.rstrip("\r\n"))
    eol = line[end_of_line:]
    body = line[:end_of_line]

    resolved = 0
    position = 0
    while position <= len(body):
        match = _HOLLERITH_START_RE.search(body, position)
        if match is None:
            break
        count = int(match.group(1))
        start = match.end()
        if start + count > len(body):
            # the constant counts past this physical line — it continues on
            # the next; rewriting it would move following line numbers
            break
        literal = body[start : start + count]
        quoted = _quote(literal)
        new_line = f"{body[: match.start()]}{quoted}{body[start + count :]}"
        if len(new_line) > _FIXED_FORM_LINE_LIMIT:
            # never widen the punch-card margin; leave this one alone
            break
        body = new_line
        resolved += 1
        position = match.start() + len(quoted)
    return body + eol, resolved


def _quote(literal: str) -> str:
    if "'" in literal:
        return '"' + literal.replace('"', '""') + '"'
    return "'" + literal + "'"
