# Plan: Dev Knowledge Blog, 2-day demo  (spec locked 2026-10-04, code freeze day 2 16:00)

Sources: specs/spec.md (locked, wins), scope/demo.md, clarify-answers.md and analyze.md (already merged into spec). Target repo: /Users/hoangphu/demo-idea. Tasks are in tasks.md.

## Approach
- Build in thin vertical slices, one per demo beat (FE + API + DB in each slice). Do the simple version of every beat first, then improve.
- **Day 1 = walking skeleton.** Beats 1-5 are clickable end to end on the deployed URL by 20:00. The simple versions:
  - plain MDX render
  - paragraph-level suggestion
  - rules-only filter
  - Approve that does a string replace and shows a badge
- **Day 2 = depth.** Day 2 adds the following, then freezes at 16:00 and spends the rest on rehearsals and the backup video:
  - span anchors
  - live LLM, cached verdicts and fake model
  - staggered animation
  - diff toggle
  - Shiki, KaTeX and self-hosted fonts
- **Riskiest dependency first.** Task 1 is a 30-min spike on the LLM spam classifier (the demo depends on a visible spam catch). The fallback is rules plus cached verdicts. Task 2 is a 30-min spike on mapping a selection to an MDX source range. Its fallback is paragraph anchors.
- **Determinism.** The demo always runs on seeded data:
  - 1 English post
  - 10 items (7 spam, 3 real)
  - a seeded author who is already logged in
  - `make reseed` before every run
- **Fallback chain.** The LLM call has a ~2 s timeout. When it fails, use cached verdicts, then the PydanticAI fake model. The page must work with the network off.
- **Classification runs in the request.** No Celery hop, because the demo needs a deterministic result in under 10 s. Celery and Redis stay in the stack but are unused.
- **Acceptance criteria ids.** R = MDX render, S = inline suggestion, F = spam filter, M = moderation panel, A = approve and revision. The number is the AC index in the spec. D1-D5 = the "Done when" items.

## Schedule
### Day 1: walking skeleton (09:00-20:00, 10 h work)
| Time | Task | Beat |
|---|---|---|
| 09:00-09:30 | T1 spike: LLM spam classifier (riskiest) | 3 |
| 09:30-10:00 | T2 spike: selection -> MDX source range | 3 |
| 10:00-11:00 | T3 scaffold FE/BE/Postgres + deploy pipeline + hello route deployed | all |
| 11:00-11:30 | T4 seed data + `make reseed` | 3-4 |
| 11:30-12:00 | T5 slides: hook quote, today screenshot, roadmap | 1, 2, 5 |
| 12:00-13:00 | lunch | |
| 13:00-14:00 | T6 MDX post render, basic (R1, R4) | 3 |
| 14:00-16:00 | T7 suggestion popup, paragraph level, anon submit + toast (S2, S3, S4, S6) | 3 |
| 16:00-17:00 | T8 Run filter, rules only, Filtered list + counter (F2, partial F1) | 3 |
| 17:00-18:00 | T9 author side panel + Approve (M1-M4) | 4 |
| 18:00-19:00 | T10 Approve applies revision + "fixed by" badge (A1, A3, A4) | 4 |
| 19:00-19:30 | T11 no-secrets check in CI / pre-deploy | all |
| 19:30-20:00 | T12 deploy + click through beats 1-5 on the deployed URL (skeleton gate) | all |

### Day 2: depth, freeze, rehearse (09:00-18:30)
| Time | Task | Beat |
|---|---|---|
| 09:00-09:30 | T13 render polish: Shiki, KaTeX, self-hosted fonts/CSS (R2, R3, R5) | 3 |
| 09:30-11:00 | T14 span-level anchors + "exactly 3 nodes" mapping (S1, S5) | 3 |
| 11:00-12:30 | T15 live LLM classifier (PydanticAI, 2 s timeout, fake model) (F1, F4, F6) | 3 |
| 12:30-13:00 | lunch | |
| 13:00-13:30 | T16 cached-verdict fallback + network-off run (F5, D3) | 3 |
| 13:30-14:15 | T17 staggered Filtered animation + counter (F3) | 3 |
| 14:15-15:30 | T18 "show changes" diff toggle + persistence + code/KaTeX after revision (A2, A5, A6) | 4 |
| 15:30-15:45 | T19 re-run no-secrets check + network-off check | all |
| 15:45-16:00 | T20 final deploy | all |
| **16:00** | **T21 code freeze**: tag release, after this only reseed or config changes | |
| 16:00-17:30 | T22 3 rehearsals in a row, ≤ 2 min each, `make reseed` between (D1, D2) | 1-5 |
| 17:30-18:00 | T23 backup video of a full run (D4) | 1-5 |
| 18:00-18:30 | buffer / stretch (Knowbie lab only if everything above is green) | |

Hours: Build items ≈ 12.5 h of the spec's 13.5 h. Spikes, scaffold, seed, slides, checks and deploy add ≈ 4.5 h. That is about 17 h before freeze, against 16.5 h available. There is no slack, so the cut order below applies.

## Risks
| Risk | Signal | Mitigation / fallback |
|---|---|---|
| LLM misclassifies or is slow (demo depends on it) | T1 spike result: < 9/10 spam caught or > 1 real fix flagged; latency > 2 s | Rules-first, cached verdicts for the 10 seeded items, fake model offline. The demo runs on the cache if the live call fails. |
| Selection -> MDX source range is unreliable | T2 fails on "exactly 3 nodes" | Paragraph-level anchors (mdast position) + seeded anchor for the demo span |
| Schedule overrun (≈17 h of work in 16.5 h) | Skeleton not deployed by 20:00 day 1 | Cut order: stretch lab -> animation simplified to fade -> diff toggle shows new text only -> span anchors fall back to paragraph |
| Deploy target not named in spec | T3 | Pick the lean-web-stack default host in T3, deploy on day 1, never on day 2 after 16:00 |
| Secrets leak into client bundle (LLM key) | T11/T19 grep fails | LLM call is server side only. CI greps `dist/` for key patterns and `VITE_*` secrets. |
| Demo state drift between rehearsals | Counter is not 7, or Lan's item is already approved | `make reseed` before every run; this step is in the rehearsal checklist |
| Network down at venue | Fonts and LLM fail | Self-hosted fonts and KaTeX CSS, cached verdicts, local run as backup, backup video |

## Conflicts
- **spec.md vs CLAUDE.md:** /Users/hoangphu/demo-idea has no CLAUDE.md, so there is no conflict. The stack follows spec.md (lean-web-stack, not Next.js).
- **spec.md vs scope/demo.md (spec wins):**
  - demo.md has EN/VI; spec is English only, with VI moved to Later.
  - demo.md uses the phrase "đúng 3 node"; spec uses "exactly 3 nodes" -> "at least 2f+1 nodes".
  - demo.md puts 1 lab in the core post; spec makes the lab a stretch goal and leaves it out of the demo beats.
  - demo.md's core path skips beats 1, 2 and 5 (slides); the spec adds them.
- **Stack note:** the spec lists Celery/Redis, but the plan runs classification in the request so the demo is deterministic. Celery stays unused.
