# Workflow test log

Brief: [hackathon-brief.md](hackathon-brief.md) · bach-workflow commit `8a90db1` · operator: Phú

## Timeline

| Step | Start | End | Duration | Notes |
|---|---|---|---|---|
| Brief drafted (idea search, before demo-scope) | — | 2026-10-03 21:04 | — | Brief written with Claude outside demo-scope |
| demo-scope · Step 0 Frame | 21:04 | 21:05 | ~1 min | Defaults picked by Claude (persona, competitors, subreddits) without asking — user asked for findings first |
| demo-scope · Step 1 feeds.py | 21:05:20 | 21:05:55 | 35 s | HN: 8 files, 320 items · Reddit: all requests "Connection refused" |
| demo-scope · Step 1 Research (5 parallel agents) | 21:06 | 21:13 | ~7 min (longest: Reddit/WebSearch agent 6.7 min) | 4× Haiku (HN extract, Trustpilot, Product Hunt, Reddit via WebSearch) + 1× Sonnet (landscape/comparison/root cause) |
| Merge + verify evidence (Claude, main session) | 21:13 | 21:14 | ~1 min | 330 rows → 65 recent persona pain → ~5 genuine on top theme after manual check |
| **Research total (Frame → findings)** | **21:04** | **21:14** | **~10 min** | Agent tokens ≈ 252k (Haiku 186k, Sonnet 66k) |
| demo-scope · Step 1 Research (human runbook) | — | — | skipped | User asked for agent findings first |

## Setup (2026-10-04, not counted in test time)

- `brew install poppler`; `~/bach-workflow/bootstrap.sh` → claude-hud, `teammateMode: tmux`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, `~/.tmux.conf`, plugin `bach@bach-workflow`
- `demo-idea` turned into a project from `lean-web-stack` (`new-project.sh demo-idea`), reference clones gitignored, `make setup` ok

## Agents (cost routing)

| Agent | Model | Job | Rows / output |
|---|---|---|---|
| HN extract | Haiku | raw HN → evidence rows | 264 rows in 44 s · 36k tokens · noisy: 131 old, only 54 recent persona pain and many off-topic quotes |
| Trustpilot | Haiku | 1–2★ competitor reviews | 17 reviews in 96 s · 40k tokens (Medium 6, Ghost 6, Substack 4, WordPress 1, dev.to 0, Hashnode 0) · shared weaknesses are support + billing, not writing/community |
| Product Hunt | Haiku | reference launches | 93 s · 44k tokens · 8 launches (OpenBlog, Tab, Git Blog; Voicetypr, Wispr Flow, VoiSistant, Voquill; Golpo, Motionvid.ai) · persona_match used "high/medium" instead of y/n (schema drift) |
| Reddit via WebSearch | Haiku | pain quotes | 40 rows in 404 s · 66k tokens · **0 Reddit URLs**, but every row labeled `r/<sub>`; several quotes look paraphrased, not verbatim. Relabeled by real domain |
| Landscape | Sonnet | landscape / comparison / root cause CSVs | 99 s · 66k tokens · 22 landscape, 15 comparison, 11 root-cause rows, ~25 sources (some vendor/listicle, some >24 months) · 7 gaps, 4 candidate differentiators |

## Difficulties

| When | Issue | Impact | Suggested improvement |
|---|---|---|---|
| 21:04 | `bach` plugin not installed on this machine; `demo-scope` has `disable-model-invocation: true`, so Claude can't start it, the user must type `/bach:demo-scope` | Setup step before research | README quick start: note the plugin must be installed before the first `/bach:*` |
| 21:04 | `pdftotext` missing (`web-research` needs it for PDFs) | Possible BLOCKED in init_run | Add `poppler` to bootstrap deps check |
| 21:05 | Reddit RSS "Connection refused" for every query (feeds.py) | W1 pain evidence from Reddit lost; fallback = WebSearch agent | feeds.py: detect a blocked source early and print a fallback hint |
| 21:06 | Ran demo-scope research by hand from the repo clone (subagents instead of the `research.js` Workflow + nested `web-research`) | Not a 1:1 run of the skill; timings are indicative | Allow model invocation for read-only phases, or ship a `--research-only` mode |
| 21:07 | Haiku extractor over-labels: persona_match=y on 235/264, quotes like "here is the entire exchange" tagged as pain | W1 counts inflated if taken raw | Add a cheap 2nd-pass relevance filter (Haiku, yes/no per row) before merge_evidence; or Sonnet low for extraction |
| 21:13 | Reddit agent labeled 40 non-Reddit rows as `r/<sub>` (provenance fabricated) | Would inflate W1 "places" count | Validate `source` against URL domain in merge_evidence.py; reject rows whose source/URL disagree |
| 21:14 | Keyword theme counting inflated: HN "comments" (meta talk about HN threads) matched the feedback theme, 12 → ~5 genuine | Gate W1 needs human/LLM check | Theme tagging by a Sonnet-low judge, not keyword or Haiku |
| 21:04 | Not in tmux (`$TMUX` empty) | Not needed for research, needed for pr-team | — |
