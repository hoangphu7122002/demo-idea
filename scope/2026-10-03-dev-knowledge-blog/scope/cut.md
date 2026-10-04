# Cut (strict) — demo angle TBD, core path from demo.md
Build first, pick story later: core path same in all 3 drafts, so cut is valid now.

| Feature | Column | Rule | Reason | Beat | Hours | Fake method |
|---|---|---|---|---|---|---|
| Inline suggestion on selected text span (popup + replacement text + optional name + anon submit + confirm) | Build | — | Core action itself | 3 | 4 | |
| Spam filter: rules (honeypot/link/keyword) + LLM classifier, Filtered list + "N spam blocked" counter | Build | — | Wow #1, must move live | 3 | 3.5 | |
| Author moderation queue + Approve button | Build | — | Approve click is beat 4 trigger | 4 | 1.5 | |
| Approve applies change -> post re-renders with inline diff + "fixed by X" credit | Build | — | Wow #2, the visible after | 4 | 3 | |
| MDX post render (markdown + code highlight + KaTeX) | Build | — | Post is the stage for beats 3-4; libs do most | 3 | 1.5 | |
| Suggest-edit diff view | Fake→merged | 2 | Covered by inline diff build item | 4 | 0 | reuse inline diff |
| Reader enters replacement text with reason | Fake→merged | 2 | Part of popup build item | 3 | 0 | reason field optional, no logic |
| Optional reader name | Fake→merged | 2 | Part of popup | 3 | 0 | plain text field |
| Anonymous submission, no login | Fake→merged | 2 | Absence of login = no work | 3 | 0 | no auth at all |
| Submit button w/ confirmation | Fake→merged | 2 | Part of popup | 3 | 0 | toast |
| Seeded sample technical post (EN/VI) | Fake | 2 | Data | 3 | | Seeded MDX post, W1 wording |
| Seeded spam + valid suggestions | Fake | 2 | Data | 3 | | 10 seeded items (7 spam) |
| Author login | Fake | 2 | Author view needed, auth not | 4 | | Seeded author, already logged in |
| LLM classifier reliability | Fake | 2 | API risk | 3 | | Live call + cached verdicts fallback |
| Spam score badge per submission | Fake | 2 | Nice visual, static | 3 | | show cached score as label |
| Author dashboard pending/approved/spam counts | Fake | 2 | Counter already built | 3 | | reuse counter |
| Suggestion on code blocks and math | Fake | 2 | Fallback paragraph-level | 3 | | paragraph-level suggestion |
| Login via GitHub | Later | 1 | Not on screen | | | |
| Email magic link login | Later | 1 | Not on screen | | | |
| Social/multi-auth | Later | 1 | Not on screen | | | |
| Akismet integration | Later | 4 | Integration off path | | | |
| Rate limit per IP | Later | 1 | Not on screen | | | |
| Spam folder restore button | Later | 1 | Not clicked | | | |
| Reject button | Later | 1 | Not clicked | | | |
| Edit suggestion before approving | Later | 1 | Not shown | | | |
| Bulk approve/reject | Later | 1 | Not shown | | | |
| Revision history list | Later | 1 | Not shown | | | |
| Diff between revisions | Later | 1 | Not shown | | | |
| Revert revision | Later | 1 | Not shown | | | |
| Contributors list at post bottom | Later | 1 | Badge enough | | | |
| Contributor reputation | Later | 1 | Not shown | | | |
| Contributor profile badge | Later | 4 | Profile | | | |
| Notify contributor email | Later | 4 | Email | | | |
| Notify author new suggestion | Later | 4 | Email | | | |
| Last revised date + changelog | Later | 1 | Not shown | | | |
| Freshness label | Later | 1 | Not shown | | | |
| Reader "outdated" flag | Later | 1 | Not shown | | | |
| Threaded comments | Later | 1 | Not shown | | | |
| Reactions | Later | 1 | Not shown | | | |
| Upvote suggestions | Later | 1 | Not shown | | | |
| Post editor for author | Later | 1 | Post is seeded | | | |
| Embeddable widget for static sites | Later | 4 | Integration | | | |
| Self-hosted option | Later | 4 | Off path | | | |
| Export as markdown/Git patch | Later | 4 | Integration | | | |
| Open GitHub PR | Later | 4 | Integration | | | |
| Rebuild webhook | Later | 4 | Integration | | | |
| Email moderation | Later | 4 | Email | | | |
| Disable suggestions per post | Later | 4 | Settings | | | |
| Permalink to suggestion | Later | 1 | Not shown | | | |
| Author highlight of pending paragraphs | Later | 1 | Not shown | | | |
| Reader view accepted highlight | Later | 1 | Covered by credit badge | | | |
| Mobile responsive | Later | 4 | Mobile | | | |
| EN/VI language toggle | Later | 4 | i18n; seed post bilingual text only | | | |
| Voice-first authoring | Later | 1 | Not shown | | | |
| Post to motion video | Later | 1 | Not shown | | | |
| giscus comparison page | Later | 1 | Only if contrast angle chosen (+30 min) | | | |

Totals: Build 5 items / 13.5 h (≤14 ok). Fake 12 (5 merged into build). Later 38.
Riskiest dep: LLM classifier — spike day 1 AM, cached verdicts fallback.

## User decisions (2026-10-04)
- Critic moves: none accepted (keep real builds; "build tới đâu rồi tính"). Moves stay available as fallbacks if behind schedule.
- Build estimate: 13.5h (user agrees).
- Stretch (after Build done): 1 Knowbie-style interactive lab component in seeded post.
