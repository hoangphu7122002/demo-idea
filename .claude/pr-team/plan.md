# PR Team plan: dev-knowledge-blog (spec: scope/2026-10-03-dev-knowledge-blog/specs/spec.md)
Start: 2026-10-04 16:49:05 · mode: in-process (no tmux, check skipped) · review budget: 3 open PRs

## Shape
Vertical 1 bước (backend API contract = backend/openapi.json) rồi horizontal (backend | frontend | ci).
Feature flag: `VITE_FEATURE_SUGGEST` / `FEATURE_SUGGEST` để PR dở dang vẫn merge được.

## Tasks
| id | folder | files (approx) | blockedBy | AC | flag | owner | PR | state |
|---|---|---|---|---|---|---|---|---|
| be-posts | backend | models/post.py, migration, routes/posts.py, seed post MDX, tests, openapi.json | - | R1 data, A6 (revision table) | FEATURE_SUGGEST | builder-1 | #4 | merged |
| be-suggestions | backend | models/suggestion.py, migration, routes/suggestions.py, tests, openapi.json | be-posts | S3, S6 (server), anon submit | FEATURE_SUGGEST | builder-1 | #5 | merged |
| be-spam-rules | backend | ai/spam_rules.py, routes run-filter, tests | be-suggestions | F1 rules, F2 | - | builder-1 | #10 | merged |
| be-seed-reseed | backend | scripts/reseed.py, seed 10 items + author | be-spam-rules | T4.1-T4.3 (script) | - | builder-1 | #13 | merged |
| be-approve | backend | services/revision.py, route approve, tests | be-seed-reseed | A1, A4, M3, M4 | - | | | todo |
| be-llm-classifier | backend | ai/spam_llm.py (PydanticAI, 2s timeout, fake model, cached verdicts) | be-approve | F1, F4, F5, F6 | - | | | todo |
| fe-mdx-render | frontend | vite.config, pages/Post, MDX plugins (Shiki, KaTeX, anchors), fonts | - | R1-R5 | - | builder-2 | #3 | merged |
| fe-suggest-popup | frontend | features/suggest/*, api client gen | fe-mdx-render, be-suggestions | S1, S2, S4, S5, S6 | VITE_FEATURE_SUGGEST | builder-2 | #9 | merged |
| fe-moderation-panel | frontend | features/moderation/* | fe-suggest-popup, be-spam-rules | M1-M4, F2 UI | VITE_FEATURE_SUGGEST | builder-2 | #12 | merged |
| fe-filter-anim | frontend | features/moderation/FilteredList | fe-moderation-panel | F3 | - | builder-2 | #14 | merged |
| fe-revision-diff | frontend | features/revision/* (jsdiff, badge, toggle) | fe-filter-anim, be-approve | A2, A3, A5 | - | | | todo |
| ci-no-secrets | .github + root Makefile | ci.yml, scripts/check-secrets.sh, Makefile reseed target | - | T11.1-T11.3, make reseed | - | builder-3 | #1 | merged |

Không có trong PR (human): slides T5, deploy T3.2/T20, freeze, rehearsals, video.

## Team
builder-1 = backend, builder-2 = frontend, builder-3 = ci (idle), reviewer-1 (backend/root), reviewer-2 (frontend, ports 4174/8001, DB app_review_r2/app_test_r2), pr-watcher.
| ci-make-reseed | root Makefile | Makefile | be-seed-reseed | make reseed | - | builder-3 | #15 | merged |
| ci-fix-workflow | .github | ci.yml | human: GitHub billing | CI runs start | - | builder-3 | | blocked (account) |
| fe-post-api | frontend | PostPage fetch via API, slug raft-consensus-in-practice | be-posts | R1 via API | - | builder-2 | #6 | merged |
| fe-shiki-langs | frontend | shiki config | - | secret scan passes | - | builder-2 | #7 | merged |
| fe-safe-mdx | frontend | MdxContent format md | - | no JSX exec from API source | - | builder-2 | #8 | merged |
| be-spam-tune | backend | ai/spam_rules.py, tests | be-spam-rules | ≤1 real fix flagged | - | builder-1 | #11 | merged |
| be-spam-tune-2 | backend | ai/spam_rules.py | be-seed-reseed | ≥9/10 spam, ≤1 real | - | builder-1 | | todo |
| fe-anim-polish | frontend | moderation panel | - | counters in sync, no blink | - | builder-2 | | in progress |
