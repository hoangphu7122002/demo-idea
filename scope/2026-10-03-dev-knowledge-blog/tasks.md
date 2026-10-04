# Tasks: Dev Knowledge Blog demo  (ordered by demo beat; see plan.md for hours)

AC ids come from specs/spec.md:
- **R1-R5** = MDX render
- **S1-S6** = inline suggestion
- **F1-F6** = spam filter
- **M1-M4** = moderation panel
- **A1-A6** = approve and revision
- **D1-D5** = the "Done when" items

Task-local checks are marked **T#.x**. Each task has at most 6 acceptance criteria.

## Day 1: walking skeleton (every beat clickable + deployed by 20:00)
- [ ] **T1 Spike: LLM spam classifier (riskiest dep)** · beat 3 · 0.5 h · AC: T1.1-T1.3
  - T1.1: 20 seeded suggestions (10 real, 10 spam) run through rules + one LLM prompt
  - T1.2: Pass = ≥ 9/10 spam caught and ≤ 1 real fix flagged; log the latency per call
  - T1.3: If it fails, switch to the fallback (rules + cached verdicts) and note it in plan.md
- [ ] **T2 Spike: selection -> MDX source range** · beat 3 · 0.5 h · AC: T2.1-T2.2
  - T2.1: remark positions are emitted as data-attrs, and selecting "exactly 3 nodes" resolves to the source offset
  - T2.2: If it fails, use paragraph anchors (mdast position) plus a seeded anchor
- [ ] **T3 Scaffold + deploy pipeline** · all · 1 h · AC: T3.1-T3.3
  - T3.1: Vite React 19 + MUI + RTK app, FastAPI, and Postgres run with one command
  - T3.2: The hello route is deployed to the demo host over HTTPS
  - T3.3: Redeploy is one command
- [ ] **T4 Seeded demo data + `make reseed`** · beats 3-4 · 0.5 h · AC: T4.1-T4.3
  - T4.1: 1 English MDX post with code, KaTeX and the sentence "exactly 3 nodes"
  - T4.2: 10 seeded suggestions (7 spam like E304, 3 real fixes) and a seeded author who is already logged in
  - T4.3: `make reseed` resets the DB to the same state in under 10 s
- [ ] **T5 Slides: hook quote, today screenshot, roadmap** · beats 1, 2, 5 · 0.5 h · AC: T5.1-T5.3
  - T5.1: Quote slide for E331, labelled as a paraphrase
  - T5.2: Static giscus/Disqus screenshot
  - T5.3: Roadmap slide with the 6 Later items from spec beat 5
- [ ] **T6 MDX post render, basic** · beat 3 · 1 h · AC: R1, R4
- [ ] **T7 Suggestion popup, paragraph level, anonymous submit** · beat 3 · 2 h · AC: S2, S3, S4, S6
- [ ] **T8 Run filter, rules only, Filtered list + counter** · beat 3 · 1 h · AC: F2, F1 (rules part)
- [ ] **T9 Author side panel + Approve** · beat 4 · 1 h · AC: M1, M2, M3, M4
- [ ] **T10 Approve applies revision + credit badge** · beat 4 · 1 h · AC: A1, A3, A4
- [ ] **T11 No-secrets-in-client check** · all · 0.5 h · AC: T11.1-T11.3
  - T11.1: A CI or pre-deploy script greps the built `dist/` for API-key patterns and secret `VITE_*` variables, and fails the build on a hit
  - T11.2: The LLM key exists only in the server env
  - T11.3: The check passes on the current build
- [ ] **T12 Skeleton gate: deploy + click through beats 1-5** · all · 0.5 h · AC: T12.1
  - T12.1: On the deployed URL, after `make reseed`, beats 1-5 can be clicked through end to end with no code edits

## Day 2: depth, freeze, rehearse
- [ ] **T13 Render polish** (Shiki, KaTeX, self-hosted fonts and KaTeX CSS) · beat 3 · 0.5 h · AC: R2, R3, R5
- [ ] **T14 Span-level anchors** · beat 3 · 1.5 h · AC: S1, S5
  - Fallback: keep paragraph anchors from T7
- [ ] **T15 Live LLM classifier** (PydanticAI, ~2 s timeout, rules first, fake model offline) · beat 3 · 1.5 h · AC: F1, F4, F6
- [ ] **T16 Cached-verdict fallback** · beat 3 · 0.5 h · AC: F5, D3
  - T16.1: A full run with the network off gives the same 7/3 split, and Lan's fix lands in Pending
- [ ] **T17 Staggered Filtered animation + counter** · beat 3 · 0.75 h · AC: F3
  - Cut fallback: a plain fade
- [ ] **T18 "Show changes" diff toggle + persistence** · beat 4 · 1.25 h · AC: A2, A5, A6
- [ ] **T19 Re-run the no-secrets check + network-off check** · all · 0.25 h · AC: T11.1, T11.3, D3
- [ ] **T20 Final deploy** · all · 0.25 h · AC: T12.1
- [ ] **T21 Code freeze at 16:00** · all · 0 h · AC: T21.1
  - T21.1: The release is tagged; after this, only reseed, config or content fixes
- [ ] **T22 3 rehearsals in a row** · beats 1-5 · 1.5 h · AC: D1, D2
  - Each run takes ≤ 2 min, with no dev tools and `make reseed` between runs
  - Any failure resets the count
- [ ] **T23 Backup video** · beats 1-5 · 0.5 h · AC: D4
  - T23.1: A full ≤ 2-min run is recorded and saved locally and in the cloud

## Stretch (only after T23, not in the demo beats)
- [ ] **T24 One Knowbie-style interactive lab in the seeded post** · not counted
