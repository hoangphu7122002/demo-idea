# Dev Knowledge Blog: 2-day demo spec  (locked 2026-10-04 · code freeze day 2 16:00)

USER        Developer with a personal technical blog (long posts, code, math); demo English only
PROBLEM     "Comment moderation overhead, managing spam/bad comments consumes valuable time"  (https://dev.to/antozanini/tech-blog-on-your-site-or-on-medium-devto-pm1, E331; paraphrased row, G1 FAIL accepted by user override)
CORE JOB    A dev blogger lets any reader suggest fixes inline without spam cleanup or Git PRs. (15 words)
DIFFERENT   Unlike Disqus, Medium and giscus, we filter spam automatically and turn approved inline suggestions into a credited revision of the post, no reader login.
MVP TYPE    single-feature web app

## Demo script
Storytelling angle TBD after build (drafts: scope/demo-pain-first.md, demo-wow-first.md, demo-contrast-first.md). Core path fixed:
1. Hook (15 s): quote slide (E331, labelled paraphrase): moderation/spam eats dev bloggers' time; fixes need GitHub login + PR (giscus).
2. Today (15 s): static giscus/Disqus screenshot: GitHub-only login blocks readers, comments sit apart from the post, spam cleaned by hand.
3. Core action (45 s): seeded English MDX post (code + KaTeX). Anonymous reader highlights "exactly 3 nodes" -> popup -> types "at least 2f+1 nodes" + optional name "Lan" -> Submit, no login (live LLM call, ~2 s timeout, rules fallback). Author clicks "Run filter": batch-classifies 10 seeded items, 7 spam move to Filtered (staggered animation), "7 spam blocked" counter.
4. Wow (30 s): author clicks Approve on Lan's fix in side panel on post page -> post re-renders clean with "fixed by Lan" badge; "show changes" toggle reveals inline diff. Spam -> clean queue -> credited revision in one take.
5. Next (15 s): roadmap from Later: embeddable widget for static sites, Git patch/PR export, revision history + diff, contributor reputation, voice authoring, post -> video.

## Build (≤ 14 h, ≤ 5 items)  total 13.5 h
| Item | Demo beat | Hours | Acceptance criteria (≤ 6) |
|---|---|---|---|
| MDX post render (markdown + code highlight + KaTeX), @mdx-js/rollup in Vite | 3 | 1.5 | 1. Seeded English post renders at /posts/<slug> with headings, prose, code block, KaTeX formula. 2. Code block syntax-highlighted (Shiki). 3. KaTeX renders, no raw `$...$` visible. 4. Each prose/code block carries a source-position anchor (data-attr). 5. Page loads with network off (fonts + KaTeX CSS self-hosted). |
| Inline suggestion on selected text span (popup + replacement + optional name + anon submit + confirm) | 3 | 4 | 1. Selecting text in prose shows popup (span-level); code blocks and KaTeX get paragraph-level suggestion next to selection within 300 ms. 2. Popup has replacement text, optional reason, optional name fields. 3. Submit works with no login; record saved with anchor (span, fallback paragraph) + text + name. 4. Confirmation toast shown after submit. 5. Selecting "exactly 3 nodes" in seeded post maps to the correct source range. 6. Empty replacement blocked with inline message. |
| Spam filter: rules (honeypot/link/keyword) + LLM classifier, Filtered list + "N spam blocked" counter | 3 | 3.5 | 1. Each suggestion classified spam/ham by rules first, then LLM (PydanticAI; fake model offline). 2. Author clicks "Run filter" on 10 seeded items: 7 spam to Filtered, 3 real fixes to Pending. 3. Items move visibly (≥300 ms transition per item, staggered) and counter shows "7 spam blocked". 4. Lan's live suggestion classified on submit (real LLM, ~2 s timeout, rules fallback) and lands in Pending. 5. LLM down/no network -> cached verdicts / fake model give same result. 6. Classification of 10 items completes < 10 s. |
| Author moderation side panel + Approve button | 4 | 1.5 | 1. Side panel on post page (seeded author, already logged in) lists Pending suggestions with quoted span + replacement + name. 2. Filtered list shown separately with count. 3. One click Approve changes status to approved. 4. Approved item leaves Pending queue. |
| Approve applies change -> post re-renders with inline diff + "fixed by X" credit | 4 | 3 | 1. Approve writes new revision of MDX source with replacement applied. 2. Post page shows new text clean by default; "show changes" toggle reveals inline diff (old struck, new highlighted). 3. "fixed by Lan" badge shown at changed span, persists with toggle off. 4. Anonymous with no name -> "fixed by a reader". 5. Code/KaTeX still render after revision. 6. Reload keeps revision (persisted in PostgreSQL). |

Build-adjacent (not counted): `make reseed` resets + re-seeds DB for rehearsals.

Stretch (after Build done, not counted, not in demo beats): 1 Knowbie-style interactive lab component in seeded post.

## Fake
| Item | Method |
|---|---|
| Seeded sample technical post (English only) | Seeded MDX post, W1 wording |
| Seeded spam + valid suggestions | 10 seeded items (7 spam, 3 real fixes, spam like E304) |
| Author login | Seeded author, already logged in |
| LLM classifier reliability | Live call + cached verdicts fallback |
| Spam score badge per submission | Show cached score as label |
| Author dashboard pending/approved/spam counts | Reuse counter |
| Suggestion on code blocks and math | Paragraph-level suggestion (not span) |
| Beats 1-2 evidence | Quote slide (E331, labelled paraphrase) + static giscus/Disqus screenshot |
| Suggest-edit diff view, reason field, optional name, anon submit, confirm toast | Merged into Build items (no extra logic) |

## Later (≥ 8)
settings · dark mode · profile editing · email prefs (notify contributor/author) · admin · payments · mobile responsive · integrations (Akismet, GitHub PR, Git patch export, rebuild webhook, embeddable widget for static sites, self-hosted option) · multi-tenant · i18n (EN/VI toggle) · Vietnamese post / VI voice · GitHub / magic-link / social login · rate limit per IP · spam restore · reject button · edit suggestion before approve · bulk approve/reject · revision history + diff + revert · contributors list · contributor reputation + badge · last-revised date / freshness label / outdated flag · threaded comments · reactions · upvote suggestions · post editor · disable suggestions per post · permalink to suggestion · voice-first authoring · post -> motion video · video embed · giscus comparison page

## Risk
Accepted (not fixed): 2 risky deps; G1 override; 13.5 h of 14 h with spikes/seeding uncounted, critic fake-moves in cut.md are schedule fallback.
LLM spam classifier (D3, demo hinges on visible spam catch) → 30-min spike first (day 1 AM): 20 seeded suggestions (10 real, 10 spam) via rules + one LLM prompt; pass = ≥9/10 spam caught, ≤1 real fix flagged; fallback: rule-based filter + cached classifier verdicts.
Second risky dep (rule says ≤1, accepted): D2 selection -> MDX source range; spike remark positions -> data-attrs; fallback: paragraph-level anchors (mdast node position), seeded anchors.

## Look & feel
- Medium-style: highlight text inline -> popup next to selection.
- Posts feel interactive like Knowbie (https://knowbie.vercel.app/c/clickhouse): interactive labs inside posts (1 lab in seeded post, stretch only), "source + why" style.
- Fonts: Crimson Pro (prose), Inter (UI), JetBrains Mono (code). Self-hosted fonts + KaTeX CSS. English only for demo.
- Clean revision by default, "show changes" toggle -> inline diff (old struck, new highlighted) + persistent "fixed by X" credit badge; Filtered pile with live "N spam blocked" counter.
- Reference screenshot: Medium highlight popup; Knowbie lesson page.

## Done when
- [ ] Beats 1–5 in ≤ 2 min, no code edits, no dev tools
- [ ] 3 rehearsals in a row pass
- [ ] Works with network off / API down (fallback: cached LLM verdicts / PydanticAI fake model, paragraph anchors, self-hosted fonts)
- [ ] Backup video recorded
- [ ] ≥ 3 of 5 judging criteria (target: usability, technical fit, growth path)

## Stack
/Users/hoangphu/demo-idea (lean-web-stack): React 19 + Vite + MUI + Redux Toolkit + MDX (@mdx-js/rollup); FastAPI + Postgres (pgvector) + Celery/Redis + PydanticAI (spam classifier, fake model offline); Shiki, KaTeX, jsdiff. Not Next.js.
