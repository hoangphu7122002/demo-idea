# S2 interview — 2026-10-04
1 Persona: dev with personal technical blog (long posts, code, math)
2 Trigger: reader finds error/outdated part in a post
3 Input: highlighted passage + reader's suggestion/comment
4 Output: new post revision with contributor credit
5 Done: author approves → post updated, credit visible
6 Today: giscus — GitHub-only login blocks readers
7 Constraints: EN/VI bilingual; non-GitHub login; no ops/moderation burden (rules + LLM spam filter); local demo
8 Look & feel: Medium-style inline highlight → popup. Posts should feel interactive like "knowbie" examples (interactive examples inside posts) — clarify reference URL.

## Candidate core-job sentences
a. A dev blogger can turn readers' inline suggestions into credited revisions without moderating spam.
b. A dev blogger can let any reader (no GitHub) suggest fixes inline without spam or Git PRs.
c. A dev blogger can publish interactive technical posts that readers improve inline without moderation work.

## Unclear
- knowbie reference (URL?), code freeze time, stack

## Round 3 (2026-10-04)
- Base: MDX + React; 1 Knowbie-style lab in seeded post; video embed = v2 (easy component).
- Anonymous comments/suggestions allowed, no login required; optional display name for credit. Spam filter (rules+LLM) becomes core.
- Inline selection suggestions limited to prose + code (not labs) for demo.
