# Research findings: dev knowledge blog (2026-10-03, 21:04–21:14)

Sources: `evidence.csv` (330 rows: HN 264, web search 40, Trustpilot 17, Product Hunt 9), `research/*.csv`, `research/summary.md`, `refs/producthunt.md`.

## Verified problems
| Problem | Strength | Evidence |
|---|---|---|
| Reader feedback doesn't improve the post (comments sit below, fixes need a Git PR, GitHub-only login) | Medium: ~5 genuine quotes from 4 places + landscape analysis | medium.com, dev.to ×2, MDN, HN (2026-05-01) · wisp.blog, merginit.com |
| Comment spam / moderation burden | Weak–medium: 2 recent quotes + older sources | dev.to, daily.dev, chriswiegman (2021) |
| Devs stop writing (time, fear of errors, no audience) | Medium in literature, weak in recent quotes (4 quotes, 2 places) | buttondown, jonbeckett, dev.to, HN |
| Technical posts go stale, only a date as signal | Weak: 1 quote + 2 articles | dasroot (32% outdated refs, snippet only), techwhirl |
| Platform lock-in / paywall (Medium, Hashnode) | Medium: 4 quotes, 3 places | daily.dev, dev.to, medium.com, typeflo |
| No reputation / credit for contributors | Inference, little direct evidence | — |

## Gaps nobody covers well
1. **Feedback → reviewed, credited edit of the post.** Comment tools (giscus, utterances, Disqus, Remark42) stop at discussion; "edit this page" means a Git PR with no credit.
2. **Per-claim freshness** visible to readers ("still valid on vX", reader-verified).
3. **Contributor credit/reputation** on a personal blog.
4. **Moderation without ops**: choices are GitHub-only, spam-prone, self-hosted, or paid.
5. **Voice → structured technical post** (code, math, series). Dictation tools (Wispr Flow, Voicetypr, Voquill) output plain text; Voicenotes drafts generic posts.
6. **Post → video inside publishing.** Remotion + Claude Code works but is code-heavy and slow to render; tools like Golpo and Motionvid.ai are not tied to a blog.

## Candidate differentiators
| | Differentiator | Gaps | Demo risk |
|---|---|---|---|
| A | Select text → suggest edit → author accepts → new post revision + automatic contributor credit | 1, 3, 4 | Low (known stack) |
| B | Freshness engine: claims tied to versions; readers confirm/dispute; staleness badge | 2 | Medium |
| C | Voice → structured technical post | 5 | High (STT + LLM pipeline, Vietnamese) |
| D | Post → motion video | 6 | High (render time); better as v2 |

## Preliminary gates (from `rules/gates.md`; W3/W4 are formally scored in the Decide step)
| Gate | Mark | Why |
|---|---|---|
| W1 Pain | Partial | Top theme (feedback doesn't improve the post) has ~5 genuine quotes from 4 places; the threshold for Pass is ≥10 quotes from ≥3 places |
| W2 Gap | Partial | Gap 1 is clear in the landscape, but 1–2★ reviews show other shared weaknesses (support, billing), not this one |
| W3 Demo moment | Likely Pass (A) | Select → suggest → accept → revision + credit is visible in under 2 minutes |
| W4 Build | Likely Pass (A) | Known stack (lean-web-stack); main risk is the diff/merge of revisions |

Indicative rule outcome: 2 Partial + 2 Pass → **NARROW** (W1 and W2 need more evidence; the human runbook on Reddit/G2 was skipped).

## Data quality caveats
- Reddit was unreachable, so there are 0 Reddit sources; the web-search agent labeled non-Reddit rows as `r/<sub>` (relabeled by domain).
- The Haiku extractor over-tagged persona and pain rows; the counts above were checked by hand.
- Several sources are vendor or listicle blogs; some are older than 24 months.
