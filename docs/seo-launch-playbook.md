# nativegate launch & discovery playbook

Everything here is ready-to-paste. Execute in order; track with the table at
the bottom. Nothing here is spam — every submission opens with what the tool
actually does and states one honest limitation.

## 0. Preconditions

- [ ] **DNS at Namecheap points to GitHub Pages** (nothing else works until this is true):
      `A @ 185.199.108.153 / 109 / 110 / 111`, `CNAME www → ravikings.github.io`.
- [ ] Confirm https://nativegate.dev serves (repo Pages already has the CNAME set).
- [ ] Ping IndexNow: `bash marketing/indexnow.sh` (Bing/Yandex/Seznam fetch).
- [ ] Google Search Console: verify the domain, submit `https://nativegate.dev/sitemap.xml`.
- [ ] Bing Webmaster Tools: verify, submit same sitemap.

## 1. Hacker News — Show HN

When: Tuesday–Thursday, 7–10am ET; block 4 hours to answer every comment within
minutes. Title (no hype, no superlatives):

```
Show HN: Ngate – turns legacy Fortran/C++ into Python APIs without rewriting them
```

First comment (your pitch; edit the personal parts):

> Hey HN — I built nativegate (https://github.com/ravikings/nativegate) after
> working with legacy petroleum engineering software: ~4,800 lines of fixed-form
> Fortran 77 with COMMON blocks and INCLUDE decks. The right answer was never to
> rewrite it — the numerics are validated — but the interface age badly and kept
> the code uncallable from anything modern.
>
> Ngate takes a legacy header/deck and generates the whole path from it: f2py or
> pybind11 bindings, the CMake build, an installable wheel, a pytest suite, a
> FastAPI service, a Dockerfile, and Kubernetes manifests. The part I care most
> about is the numerical golden record: it records the answers the bindings
> return today and fails any future change that moves them, so modernization
> stays provable.
>
> The honest limitation: Fortran services are one native call at a time per
> process — COMMON blocks are process-global storage, so the generated service
> holds a lock across each call. Capacity comes from replicas, not concurrency.
> Derived-type support is narrow (all-scalar components, same-file types).
> Supported parts: https://nativegate.dev
>
> Feedback I'd value most: whether the golden-record verify feels like the right
> acceptance contract for modernization, and what I'm missing for your legacy
> codebase specifically.

Rules from the launch guides: never ask for upvotes, reply to every substantive
comment within 10–15 minutes for the first 2 hours, concede correct criticism,
don't repost if flagged (email hn@ycombinator.com instead).

## 2. Reddit (one post per subreddit, tuned)

- r/Fortran — technical angle: "Generated f2py bindings from fixed-form F77 decks
  with COMMON blocks — full pipeline incl. numerical regression checks"
- r/Python — general angle: "I built a tool that makes 40-year-old Fortran
  importable from Python (and deployable as an API)"
- r/scientificcomputing, r/oceanography/physics-adjacent — lead with the
  worked example, not the tool.
- r/legacy_it, r/oilindustry — problem framing: "how are you handling your
  1990s property correlations?"

## 3. dev.to / lobsters cross-posts

Republish `fortran-reservoir-model-to-python-api.html` and
`modernizing-legacy-engineering-software.html` as canonical-linked articles.
Lobsters: submit the F2PY evaluation post (regular link).

## 4. GitHub awesome-list PRs

Status as of 2026-09-19:

| Target | Section | Status |
|---|---|---|
| punkpeye/awesome-mcp-servers (95k★) | Developer Tools (agent-fast-track: 🤖🤖🤖 in PR title) | **PR #14712** open; bot requires Glama listing + badge (see Glama step below) |
| appcypher/awesome-mcp-servers (5.7k★) | Tools & Utilities | blocked via API (PR creation denied, issues disabled); branch ready on fork — submit manually at https://github.com/appcypher/awesome-mcp-servers/compare/main...ravikings:awesome-mcp-servers:add-nativegate |
| rabbiabram/awesome-fortran (415★) | Compiling & building | **PR #25** opened 2026-09-19 |
| brandonhimpfen/awesome-fortran | Interoperability (already lists f2py) | **PR #22** opened 2026-09-19 |
| nschloe/awesome-scientific-computing (1.6k★) | bottom of category | **wait until 30 days after launch**, then PR with format `[package](link) - Description. [Python, MIT, GitHub]` |
| feststelltaste/awesome-agentic-software-modernization | case studies (NOT tools) | later, as a case-study entry |
| fffaraz/awesome-cpp (73k★) | propose Interop section | later, once repo has adoption evidence |

## 4.1 Glama listing (unblocks the punkpeye PR — 15 minutes, browser only)

The punkpeye bot enforces a Glama badge on every entry. For nativegate:

1. Sign in at https://glama.ai/mcp/servers with GitHub OAuth.
2. Submit the repo; add the generated service Dockerfile (`services/petro_api/Dockerfile`)
   for their startup/introspection check (the /mcp endpoint must start).
3. Once listed, update PR #14712's line so the badge sits between the repo link and
   the emojis — exactly like its neighbors:
   `- [ravikings/nativegate](repo) [![ravikings/nativegate MCP server](https://glama.ai/mcp/servers/ravikings/nativegate/badges/score.svg)](https://glama.ai/mcp/servers/ravikings/nativegate) 🐍 🏠 🍎 🪟 🐧 - ...`

## 4-bis. brandonhimpfen PR was closed, not merged

PR #22 at brandonhimpfen/awesome-fortran was closed without merge. Do not
re-submit without a change of substance; ask the maintainer what the
objection was first.

Maintainer feedback 2026-09-22: nativegate lacks demonstrable "maturity,
independent adoption, recognition, ecosystem significance". Bare list
submissions will keep failing for the same reason. Strategy moved to
[significance-plan.md](significance-plan.md): pause further list
submissions until PyPI publication, one upstream-accepted PR, one
documented external user, and a DOI exist.

## 5. Directories (manual, one clean listing each — skip everything else)

- AlternativeTo — as a "Fortran↔Python modernization tool"
- LibHunt, SaaSHub, OpenAlternative, DevHunt (dev-tool focused, follow links)

## 6. Tracking

| Channel | Done | Date | URL |
|---|---|---|---|
| DNS fix | ☐ | | |
| IndexNow ping | ☐ | | |
| GSC verify + sitemap | ☐ | | |
| Bing WMT | ☐ | | |
| Show HN | ☐ | | |
| punkpeye/awesome-mcp-servers (punkpeye) PR | ☑ — Glama listing confirmed, badge added 2026-09-22, checks green; awaiting maintainer merge | 2026-09-19 | https://github.com/punkpeye/awesome-mcp-servers/pull/14712 |
| nativegate on PyPI | ☑ — published 2026-09-22 (0.1.0; 0.1.1 on 2026-09-23 with the specfun readme fix) | 2026-09-22 | https://pypi.org/project/nativegate/ |
| showcase: specfun-py | ☑ CI green on pristine netlib bytes via nativegate dialect: cd (0.1.3-0.1.6 loop); PyPI publish pending the user's one-time pypi.org claim + Trusted Publisher, then re-cut as v1.0.2 | 2026-09-23 | https://github.com/ravikings/specfun-py |
| nativegate defect loop (D9-D11) | ☑ all three specfun-contact defects fixed and released: 0.1.2 (D9), 0.1.5 (D10 labels), 0.1.6 (D11 CMake guard); config unknown-key errors in 0.1.4 | 2026-09-23 | docs/significance-plan.md Phase 2 evidence |
| quadpack probe + D14 fix | ☑ external/callback dummies refused, not mis-typed (0.1.8); D15 Hollerith-vs-gfortran scoped; callback support ROADMAP 3.5 | 2026-09-23 | docs/significance-plan.md Phase 2 evidence |
| D15 Hollerith fix | ☑ front-door resolution, QUADPACK parses under default backend (0.1.9); all contacted netlib idioms now handled or refused honestly | 2026-09-23 | docs/significance-plan.md Phase 2 evidence |
| awesome-fortran (rabbiabram) evidence update | ☑ commented 2026-09-23 with PyPI + specfun-py; no re-ping | 2026-09-23 | https://github.com/rabbiabram/awesome-fortran/pull/25#issuecomment-5794131182 |
| awesome-mcp-servers (appcypher) PR | ☐ (manual click) | | branch pushed to fork; API denies creation |
| awesome-fortran (rabbiabram) PR | ☐ | 2026-09-19 | https://github.com/rabbiabram/awesome-fortran/pull/25 |
| awesome-fortran (brandonhimpfen) PR | ☐ | 2026-09-19 | https://github.com/brandonhimpfen/awesome-fortran/pull/22 |
| awesome-scientific-computing (30-day) | ☐ | | |
| Reddit posts | ☐ | | |
| dev.to / lobsters | ☐ | | |
| Directories (4) | ☐ | | |
