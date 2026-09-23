# Making nativegate "not have to be convinced about"

Feedback received 2026-09 (awesome-fortran maintainer, closing PR #22 / passing on #25):

> it does not currently demonstrate the maturity, independent adoption,
> recognition, or broader ecosystem significance required for inclusion ...
> technical functionality or active development alone does not establish
> comparable significance ... Make NativeGate significant enough that the
> next person doesn't have to be convinced.

Translating that: the four claims the maintainer named are all things
**other people do to your project**, not things you can say about it. This
doc is the plan for making each of them observably true.

## Baseline (2026-09-22)

| Signal | Now | Target (90 days) |
|---|---|---|
| PyPI package | Not published (git+https only) | Published, semver, wheels |
| Stars / forks / open issues from others | 0 / 0 / 0 | 3+ issues or 25+ stars |
| Independent users | 0 | 2 documented (not self) |
| Recognition (citations, talks, upstream mentions) | 0 | 1 Zenodo DOI + 1 community thread + 1 benchmark note |
| Ecosystem relationship (f2py) | None stated | Explicit "on top of f2py, not instead of"; 1 upstream contribution |

## Why this matters strategically

Every fancy listing (awesome lists, IndexNow, GSC) produces *impressions*.
But the maintainer gate is *independent adoption*, and no amount of
directory traffic substitutes for one real user who did not write the
tool. The current playbook's section 3 (list submissions) should be
paused: we cannot manufacture significance, only make it possible and get
out of the way. One accepted external PR outweighs twenty awesome-list
entries.

## Phase 1 — Remove "not mature" (2 weeks)

1. **Publish to PyPI.** `pip install nativegate` with wheels, a changelog
   (keep a CHANGELOG.md from now on), and a version that increments.
   A code generator installed by `git+https#subdirectory=` reads as
   pre-release. This is the single cheapest signal fix.
2. **Zenodo DOI** wired to GitHub releases so every release gets a citable
   archive. This is what a Fortran academic reads as "maturity."
3. **CI that a reviewer can trust without reading the design doc:**
   GitHub Actions badge running the real build (cmake + gfortran +
   clang++) and golden verification on every push. Coverage badge if
   available. The repo already does real builds; make that visible at a
   glance.
4. **Trim the README's self-auditing honesty front and center** — keep it.
   The defect list is a credibility asset; pair it with a one-line
   "what this does today" so a maintainer gets scope in 10 seconds
   instead of 10 minutes.

## Phase 2 — Create one independent user (the hard part, 30–60 days)

Do not wait for organic users; go create the first two deliberately.

1. **Third-party showcase wraps.** Pick 2 well-known public Fortran/C++
   libraries with real users (candidates: QUADPACK-derivative packages,
   SLATEC-derived codes, open-source ODE/PDE cores) and produce a
   published, maintained python package for each, built *by nativegate*,
   on PyPI. These are independent artifacts proving the pipeline end to
   end on code you didn't write. A maintainer can download and run them.
2. **One upstream acceptance.** Find a single real project whose Python
   bindings could be generated (or improved) by nativegate, open a PR in
   *their* repo that swaps hand-written bindings for (or just simplifies
   to) nativegate output. One merged third-party PR "using nativegate"
   is the strongest possible adoption evidence and it will be the origin
   of every future answer to "who uses this?".
3. **Community presence, not list placement.** Join the actual Fortran
   Python interop conversations where the users are:
   - fortran-lang Discourse / Fortran-lang community channels
   - SciPy Discourse (f2py maintainers read it)
   - r/fortran
   Show up as answering how-to questions about f2py/interop first; the
   SIG mentions nativegate when it genuinely answers someone's problem.
   One thread that ends with "this solved my case, thanks" is an
   adoption record.

## Phase 3 — Recognition and ecosystem significance (60–90 days)

1. **Benchmark note vs hand-rolled f2py.** Take one of the Phase-2
   showcases and publish measured numbers: hours and lines to expose N
   routines by hand vs nativegate, plus identical-answers proof (golden
   check makes this trivial and is itself a differentiator). Post as an
   article; this gives maintainers something citable and concrete.
2. **Contribute the relevant patches upstream to f2py / SciPy** if any of
   the FINDINGS.md defects turn out to be f2py limitations (module
   nesting, COMMON-block state, etc.). Being *visible in the f2py
   ecosystem as contributors* converts the tool from "competing,
   unverifiable claims" to "built by people fixing the boundary itself".
3. **One venue talk:** FortranCon or a SciPy-conference lightning talk
   slot. Recording gets cited; talk abstracts get indexed.
4. **Then** re-approach the curated lists (awesome-fortran protocols,
   awesome-cpp "Interop" section, the HEAD of this playbook's table) with
   the evidence in hand: PyPI link, DOI, upstream PR, benchmark. Re-
   filing now would reproduce the same outcome.

## The test that matters

Before any submission, ask the question the maintainer is really asking:

> "If someone Googles this project, how many artifacts exist that I did
> not write and cannot fake — packages with install counts, threads I
> didn't start, repos depending on it, a DOI?"

Every phase above is an artifact of exactly that kind. Re-read the
rejection only after at least: PyPI published, one upstream-accepted PR,
one user testimonial I didn't write, one DOI.
