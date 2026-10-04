# Demo script · angle: contrast-first (≤120 s)

Setup: split screen. LEFT = same post on static blog + giscus. RIGHT = our app. Same input both sides: reader spots "đúng 3 node" error + 7 seeded spam/bot items (E304-style).

| # | Beat | s | Script |
|---|---|---|---|
| 1 | Hook | 15 | On screen: "Comment moderation overhead, managing spam/bad comments consumes valuable time" (E331, dev.to, 2024-10-10; W1 notes it is paraphrased). Say: "Every dev blogger knows this. Watch the same reader fix on both sides." |
| 2 | Today | 15 | LEFT: reader clicks giscus → "Sign in with GitHub" wall → gives up. Author's inbox: 7 bot comments to delete by hand. Fix never lands. |
| 3 | Core action | 45 | RIGHT: anonymous reader highlights "đúng 3 node" → popup → types fix + optional name "Lan" → Submit. No login. Same 7 spam items hit the queue. |
| 4 | Wow | 30 | RIGHT on screen: filter (rules + LLM) moves 7 spam to "Filtered" live, counter "7 spam blocked"; author clicks Approve once → post re-renders with diff + "fixed by Lan" credit. LEFT still: login wall + 7 spam. |
| 5 | Next | 15 | Roadmap (Later): revision history/revert, contributor list, GitHub/email login, bulk moderation, video embeds, more interactive labs. |

Total: 120 s. Impact lands by ~75 s (beat 4 start).
Risk: selection→Markdown mapping; fallback = suggest on whole paragraph (beat 3 still one action).
Fallback for LLM: cached classification.
