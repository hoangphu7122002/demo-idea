# Demo script — pain-first (≤120 s)
Core job: A dev blogger can turn anonymous readers' inline fixes into credited revisions without moderating spam.

| # | Beat | s | Script / on screen |
|---|---|---|---|
| 1 | Hook | 15 | Full-screen quote (E331, dev.to, 2024-10-10): "Comment moderation overhead, managing spam/bad comments consumes valuable time." VO: "Every dev blogger knows this. And the readers who could fix your post? They can't even comment." |
| 2 | Today | 15 | giscus box on a static blog: "Sign in with GitHub" wall + Disqus-style feed of bot spam (seeded, E304 wording). VO: "Today: GitHub login or a spam pile. Fixes need a PR." |
| 3 | Core action | 45 | Seeded MDX post (code + 1 lab). Anonymous reader highlights "exactly 3 nodes" → popup → types "should be 2f+1 nodes", name "Linh" → Submit. No login. |
| 4 | Wow | 30 | Author queue, split screen: 10 incoming items, filter (rules + LLM, cached fallback) live-sorts 7 spam → "Filtered", 3 real fixes stay. Author clicks Approve on Linh's → post re-renders: inline diff highlight + "Fixed by Linh" credit badge. Zero manual moderation. |
| 5 | Next | 15 | Roadmap slide (Later): EN/VI posts, suggestions inside labs, voice authoring, post→video, revision history. VO: "Your readers become co-authors; spam never reaches you." |

Total: 120 s. Impact (wow) lands by ~105 s; pain stated at 0 s.
Fallback: if remark source-position mapping fails, beat 3 = suggest on whole paragraph (same flow).
Caveat: E331 is a paraphrased row, not verbatim (W1 FAIL); swap for a verbatim quote if found.
