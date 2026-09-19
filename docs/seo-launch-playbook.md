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
| punkpeye/awesome-mcp-servers (95k★) | Developer Tools (agent-fast-track: 🤖🤖🤖 in PR title) | **PR #14712** opened 2026-09-19 |
| appcypher/awesome-mcp-servers (5.7k★) | Tools & Utilities | blocked via API (PR creation denied, issues disabled); branch ready on fork — submit manually at https://github.com/appcypher/awesome-mcp-servers/compare/main...ravikings:awesome-mcp-servers:add-nativegate |
| rabbiabram/awesome-fortran (415★) | Compiling & building | **PR #25** opened 2026-09-19 |
| brandonhimpfen/awesome-fortran | Interoperability (already lists f2py) | **PR #22** opened 2026-09-19 |
| nschloe/awesome-scientific-computing (1.6k★) | bottom of category | **wait until 30 days after launch**, then PR with format `[package](link) - Description. [Python, MIT, GitHub]` |
| feststelltaste/awesome-agentic-software-modernization | case studies (NOT tools) | later, as a case-study entry |
| fffaraz/awesome-cpp (73k★) | propose Interop section | later, once repo has adoption evidence |

Entry text used (tune per list's format):

```
- [nativegate](https://github.com/ravikings/nativegate) - Generates f2py/pybind11 bindings, a Python package, a FastAPI service, Docker/Kubernetes artifacts, and numerical golden-record regression checks from legacy C++/Fortran code. MIT.
```

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
| awesome-mcp-servers (punkpeye) PR | ☐ | 2026-09-19 | https://github.com/punkpeye/awesome-mcp-servers/pull/14712 |
| awesome-mcp-servers (appcypher) PR | ☐ (manual click) | | branch pushed to fork; API denies creation |
| awesome-fortran (rabbiabram) PR | ☐ | 2026-09-19 | https://github.com/rabbiabram/awesome-fortran/pull/25 |
| awesome-fortran (brandonhimpfen) PR | ☐ | 2026-09-19 | https://github.com/brandonhimpfen/awesome-fortran/pull/22 |
| awesome-scientific-computing (30-day) | ☐ | | |
| Reddit posts | ☐ | | |
| dev.to / lobsters | ☐ | | |
| Directories (4) | ☐ | | |
