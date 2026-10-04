# Demo script — angle: wow-first (≤120 s)
Open on the finished result, then rewind to show how it got there.

| # | Beat | s | Script / on screen |
|---|---|---|---|
| 1 | Hook (wow flash + W1 quote) | 15 | Flash the end state: published post with a highlighted revised line + "Fixed by Anonymous reader" badge, and a counter showing "7 spam blocked". Overlay the W1 quote: *"Comment moderation overhead, managing spam/bad comments consumes valuable time"* (E331, dev.to, 2024-10-10). VO: "This post fixed itself overnight. Let's rewind." |
| 2 | Today | 15 | Same post with giscus: "Sign in with GitHub" wall. A reader spots "đúng 3 node", which is wrong, and leaves. Author inbox full of bot spam (E304). VO: "Readers who aren't on GitHub can't help. Bots still get through." |
| 3 | Core action | 45 | One action, done live: an anonymous reader highlights "đúng 3 node" in the seeded EN/VI post → popup → types "ít nhất 3 node" + reason + optional name "Linh" → Submit. Confirmation: "Sent to author". |
| 4 | Wow (visible) | 30 | Split screen. Left: author queue. 10 seeded items get sorted live (rules + LLM): 7 spam items go to Filtered with a score badge, 3 real fixes stay. Right: author clicks Approve on Linh's fix → post updates with an inline diff (strikethrough → new text) and the badge "Fixed by Linh", the exact frame from beat 1. |
| 5 | Next | 15 | Roadmap card (Later): voice/video suggestions, labs inline edits, email/GitHub login opt-in, contributor reputation, revert/revision history, bulk moderation, Akismet fallback, hosted multi-blog. VO: "Any reader can fix your blog, and the bots can't." |

Total: 120 s. Impact lands by ~15 s (flash) and is paid off at ~105 s.

Fakes: seeded post + 10 seeded submissions (spam worded like E304), LLM live call with cached fallback, no auth (anonymous by design).
Risk: highlight→Markdown offset mapping (remark position spike, 30 min); fallback = paragraph-level suggestion, and beat 3 highlights the whole paragraph.
