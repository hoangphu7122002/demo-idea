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
| Human runbook done by Claude instead (10-04) | 12:33 | 12:38 | ~5 min | Reddit/G2/Capterra all 403 from this machine; search engine returns no Reddit links. Got 8 rows: 4 outdated-post (all >24 months), 4 Disqus moderation reviews |

## Usage

| Checkpoint | Weekly usage % | Note |
|---|---|---|
| Before demo-scope | ~70% used (30% left) | budget for project: 20%, keep 10% for Monday |
| After demo-scope | | |
| After pr-team | | |

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
| 10-04 | Human runbook can't be delegated: Reddit, G2, Capterra block agents (403) and search engines rarely return Reddit threads | W1/W2 stay Partial unless a human browses | Keep H1/H4 as human-only, or a logged-in browser tool |
| 10-04 | Operator uses the Claude Code VS Code extension, not the CLI; pr-team preflight requires tmux and bootstrap forces `teammateMode: tmux` | Hard for IDE users; resolved by preparing a detached `tmux` session `work` running `claude`, attached from the VS Code terminal | pr-team: make tmux optional (in-process teammates), bootstrap: default `teammateMode: auto` |

## pr-team (2026-10-04)

Spec: scope/2026-10-03-dev-knowledge-blog/specs/spec.md · plan: .claude/pr-team/plan.md · review budget 3

| Step | Start | End | Duration | Notes |
|---|---|---|---|---|
| Preflight | 16:49:05 | 16:49 | <1 min | Not in tmux → in-process per user's pre-set answer, tmux check skipped. teams=1, gh ok, main clean |
| Plan (12 tasks, vertical→horizontal) | 16:49 | 16:50 | | User approved. 3 builders (backend/frontend/ci), 1 reviewer, 1 watcher |
| Spawn | 16:50:42 | 16:51 | | Lead has no TaskCreate tool → task queue given in prompts + plan.md (deviation from skill) |

### PRs
| PR | Task | Builder | Opened | Merged | Review rounds | Notes |
|---|---|---|---|---|---|---|
| #1 | ci-no-secrets | builder-3 | 16:52 | 16:57 | 1 | skipped plan approval; CI not yet confirmed; make reseed fails until be-seed-reseed |
| #3 | fe-mdx-render | builder-2 | 16:56 | 16:57 | 0 | local lint/typecheck/test/build pass; FE queue then blocked on backend |
| #4 | be-posts | builder-1 | 17:00 | 17:09 | 2 | local ruff/mypy ok, pytest 13/14 (test_chat Redis port, unrelated); slug differs from FE fixture |
| #5 | be-suggestions | builder-1 | 17:11 | 17:13 | 0 | make gen by builder OK (reused worktree); 10 tests |
| #6 | fe-post-api | builder-2 | 17:11 | 17:13 | 0 | 14 tests, build pass |
| #7 | fe-shiki-langs | builder-2 | 17:20 | 17:27 | 0 | fixes main secret-scan false positive |
| #8 | fe-safe-mdx | builder-2 | 17:20 | 17:27 | 0 | XSS hardening: format md |
| #9 | fe-suggest-popup | builder-2 | 17:25 | 17:27 | 0 | interactive → needs flow screenshots; budget hit 3/3 |
| #10 | be-spam-rules | builder-1 | 17:31 | 17:42 | 0 | first PR under enhanced reviewer; tests not re-run after rebase |
| #11 | be-spam-tune | builder-1 | 17:47 | 17:48 | 0 | not reported to lead yet |
| #12 | fe-moderation-panel | builder-2 | 17:48 | 17:52 | 0 | first PR for reviewer-2; Approve disabled |
| #13 | be-seed-reseed | builder-1 | 17:54 | 17:56 | 0 | 7 spam caught by rules alone; reseed ~6 s |
| #14 | fe-filter-anim | builder-2 | 17:55 | 17:56 | 0 | built stacked locally, rebased after #12 |
| #15 | ci-make-reseed | builder-3 | 18:00 | 18:01 | 0 | migrate+reseed 8 s wall (limit 10 s) |

### Issues / deviations
- Lead lacks TaskCreate/TaskUpdate: shared task list not created; builders get ordered queues in prompt.
- 16:51 reviewer-1 exited immediately (no PRs yet) instead of waiting; lead will re-dispatch per PR.
- 16:52 Lead planning error: bundled Makefile reseed target into ci-no-secrets (2 intents, dep on unmerged script). reviewer-1 caught it; reseed split into new task ci-make-reseed blockedBy be-seed-reseed.
- 16:54 PR #1: user commented on GitHub 'drop secret script' (Claude can check secrets itself). Watcher escalated correctly; lead asked user → keep reseed only, drop script. builder-3 had already applied lead's earlier opposite fix (removed reseed, opened+closed PR #2) → rework. Lesson: lead routed fix before reading PR comments; watcher + lead both routing = race. Also: ci.yml paths filter skips root/scripts/.github changes, so CI never ran on PR #1.
- 16:55 builder-3 blocked: auto-mode classifier denied removing secret scan ('Security Test Removal') even though user decided it via AskUserQuestion in lead session — decision relayed by lead doesn't count. Builder correctly did not work around it. Needs human action.
- 16:56 builder-2 idle after PR #3: whole FE queue blocked on backend merges (vertical shape → FE builder starves while backend is serial). Plain-text spans lack anchors (needed later for S1/S5).
- 16:58 User merged #1 (secret scan kept, reseed removed) and #3 at 16:57; #2 closed. All GitHub Actions runs = startup_failure (workflow file issue, pre-existing) → CI has never actually run; new task ci-fix-workflow → builder-3.
- 17:00 ci-fix-workflow: not a ci.yml bug — minimal probe workflow also startup_failure → account-level (likely billing/minutes on private repo). Needs human. Paths-filter change parked until CI can run.
- 17:00 builder-1 couldn't reach 'team-lead' via SendMessage (agent prompt assumes teams naming; lead is main session) → PR URL only arrived via hand-back; skipped plan approval. Backend first PR took ~9 min agent time (slow test suite ~2 min).
- 17:00 pr-watcher reported budget hit (3 open) from stale state.json; actual open = 1 (#4). Lead corrected it.
- 17:02 PR #4 blocker: contract job needs openapi.json + frontend/src/api/schema.d.ts regenerated together (make gen with .env). Plan gap: lead didn't name schema.d.ts as the shared contract file. Now allowed in backend PRs. Slug decision: raft-consensus-in-practice; FE fixture to follow.
- 17:02 Coordination overhead: PR #4 fix produced ~5 cross-agent messages (reviewer→builder, builder→lead ask, watcher re-route, reviewer status) for a 1-file contract decision the plan should have pre-made.
- 17:03 2nd classifier block: builder-1 'make gen' (cp .env + npm ci + gen) denied as 'Modify Shared Resources'. Lead approval doesn't count; lead won't run it (laundering). Needs user: allow rule or run it. Pattern: auto-mode blocks cross-folder/contract steps the skill expects builders to do.
- 17:05 User asked lead to add allow rule for make gen; lead edit of .claude/settings.json DENIED by classifier (Self-Modification). builder-1 also still denied. User must edit settings by hand.
- 17:05 builder-1 retried on lead's (wrong) claim that rule was added; denied again. Lead error: sent 'rule added' before the edit result came back.
- 17:06 3rd denial for make gen even with allow rule ('Auto-Mode Bypass'; worktree needs cd prefix so rule doesn't match). Lead stops retrying; human runs make gen. Finding: in auto mode, builders in worktrees can't run root-level codegen; allow rules don't match 'cd <wt> && ...'.
- 17:07 Human ran make gen manually in worktree (first failed: worktree lacks frontend/node_modules → npm ci needed). Pushed 9faade8. PR #4 blocker took ~25 min of wall time for an 80-line generated file.
- 17:08 Auto mode exited (user). Fix for next backend PRs: builder-1 reuses wt-be-posts worktree (has .env + node_modules), runs make gen itself. Skill gap: new worktree per task = no node_modules/.env → codegen fails.
- 17:09 PR #4 re-review: no blockers (contract diff empty, pytest 14/14). Ready for human merge.
- 17:10 Lead missed #4 merge (17:09) for minutes: watcher didn't report it and lead doesn't poll by design. User had to ask. Builder-1 idle meanwhile. Added task fe-post-api for builder-2 (was idle).
- 17:10 ROOT CAUSE watcher silent on merges: pr_poll.py open_prs() uses 'gh pr list --state open', so a merged PR drops out of the poll set before its MERGED pr_state is ever diffed → 'pr_state MERGED' event can never fire. state.json still shows #1/#3/#4 OPEN. Skill bug (pr_poll.py:53, :135). Fix: also poll PRs known in state.seen that are no longer open, emit MERGED/CLOSED, then drop them.
- 17:17 PR #6 merged by human BEFORE reviewer finished → main red (secret-scan false positive: runtime Shiki bundles all langs, emacs-lisp 'ask-...' matches sk-) + stored-XSS risk (MDX compile of DB source). Reviewer messaged builder-2 AND builder-3 with competing fixes; lead deduped (builder-2 owns). New tasks fe-shiki-langs, fe-safe-mdx. Lesson: pre-review is too slow (~6 min) vs human merge pace; no CI gate since Actions dead.
- 17:18 builder-3 had started regex edit before stand-down; reverted, nothing pushed. Fallback regex tested: (^|[^A-Za-z0-9-])(sk-ant-...|sk-...). Agent duplication caused by reviewer messaging 2 builders directly.
- 17:19 User again had to tell lead #5 merged (17:13). Lead patched pr_poll.py one_pass(): re-poll PRs whose last seen state is OPEN but no longer in open list. Dry run on state copy emits MERGED for #1,#3,#4,#5,#6. Watcher picks it up on next poll.
- 17:19 PR #5 review loop worked end to end: human comment 'logic not in controller' → watcher routed → builder-1 fix 6c3a957 (services/suggestions.py) → 'addressed in' reply; fix is in main. Lead wasn't told (watcher→builder direct). Thread left unresolved. '1 check passed' = GitGuardian only, not ci.yml.
- 17:20 Watcher fix confirmed live: watcher reported merges #1,#3,#4,#5,#6 after patch.
- 17:20 User flagged: no guarantee UI renders correctly (only unit tests, no app run). Added visual check to reviewer: vite preview + playwright screenshot of post page, reviewer reads PNG. Skill gap: pr-reviewer has no 'run the app / look at it' step.
- 17:21 User rule: screenshots required for interactive changes; skip for small changes. Reviewer drives flow with Playwright + real backend; builder-2 adds data-testids.
- 17:25 Review budget hit (3/3: #7,#8,#9). builder-2 self-paused correctly.
- 17:26 User: screenshots must be in PR comments. gh can't upload images → reviewer pushes PNGs to orphan branch pr-shots and embeds blob?raw=true links.
- 17:27 #7,#8,#9 merged before reviewer's visual/interactive check finished → switched to post-merge check on main. Human merge pace > reviewer pace (again).

### Pre-review latency (UTC, from gh)
| PR | Opened | First review/comment | Merged | Merged before review? |
|---|---|---|---|---|
| #3 | 09:56:00 | 09:57:56 | 09:57:00 | yes |
| #4 | 10:00:04 | 10:01:53 | 10:09:12 | no (2 rounds) |
| #5 | 10:10:51 | 10:12:44 | 10:13:16 | no |
| #6 | 10:11:41 | 10:16:58 | 10:13:46 | yes |
| #7 | 10:19:11 | 10:25:33 | 10:26:43 | no |
| #8 | 10:20:10 | 10:25:35 | 10:26:51 | no |
| #9 | 10:24:47 | none | 10:26:59 | yes |
Causes: reviewer is push-only (no poll; waits for lead relay) · exits after each review, resumed per message · single reviewer, serial queue · full local checks (checkout, install, pytest ~2 min, build, screenshots) · human merges in ~1–7 min. Fix ideas: builder pings reviewer directly on PR open; reviewer posts "pre-review in progress" immediately + quick diff pass first; watcher triggers reviewer on new PR; human waits for "no blockers" comment/label.
- 17:30 Reviewer enhanced (archive/bach-workflow pr-reviewer.md + pr-builder.md step 7): self-polls gh every 60s, never ends turn; pass 1 fast diff-only ≤90s with 'pre-review:running' label + 'pre-review fast:' comment; pass 2 checks + screenshots (in PR description via pr-shots branch) + 'pre-review:ok/blocked' label. Builders ping reviewer first. Running reviewer-1 told to switch; installed plugin cache (0.3.0) still old until plugin update.
- 17:31 builder-2 idle again (FE chain gated on be-spam-rules). Backend serial chain = critical path.
- 17:31 Post-merge check on main 672b1c1 passed: post renders, suggest flow works with real backend (anchor 455-470). Screenshots embedded in PR #9 description via pr-shots/main-1729/. First end-to-end visual proof.
- 17:39 PR #10 enhanced reviewer timing: opened 10:30:55 UTC → running 10:33:01 (2m06s, reviewer was finishing post-merge check) → fast 'no blockers' 10:33:17 (16s pass). Deep pass still running at 10:39:44.
- 17:41 PR #10 final: no blockers. Watcher surfaced rule false positives (substring keywords, single hit = threshold, TLD rule flags socket.io). Lead proposes merge + follow-up be-spam-tune.
- 17:41 reviewer-1 #10 final: pytest 29/29, contract clean. Shared app_test DB contended (builder + reviewer run pytest concurrently → transient failures). Parallel reviewers would need separate test DBs.
- 17:42 reviewer-1 now runs a background 60s poll job that wakes it on unlabelled PRs (loop works without lead relay). Uses scratch DB app_review for interactive checks. #7 secret scan passes again, #8 XSS hardening verified.
- 17:42 #10 merged 17:42. Added reviewer-2 (general-purpose agent + new pr-reviewer.md, since plugin cache is old), split by folder, separate ports/DBs/worktrees. builder-1: be-spam-tune then be-seed-reseed. builder-2: fe-moderation-panel.
- 17:48 #11 merged 28 s after open (10:47:43→10:48:11 UTC), no review at all (reviewer-1 poll is 60 s). Post-merge check requested. Human merge speed is the binding constraint on pre-review value.
- 17:50 User rule: merged PR → reviewer stops (no post-merge review unless asked). Human decides risk by merging. pr-reviewer.md updated; #11 post-merge check cancelled.
- 17:51 fe-filter-anim built locally on top of #12 (02e28c0), waiting for #12 merge to rebase + open PR.
- 17:52 Post-#11 probe (before cancel): 0/10 real flagged but spam recall 7/10 (link-only + money spam pass) → over-correction. Queued be-spam-tune-2 after reseed; seeded spam must be caught by rules alone. pytest on main 35 errors, suspected shared app_test DB → builders get own test DB. Stray vite preview on 4173 from an agent worktree (port collision).
- 17:54 builder-1: shared Postgres :5442 showed crash-recovery under concurrent pytest from builders + 2 reviewers → test errors were infra, not code. Private DB app_test_b1 passes. Skill gap: no per-agent test DB isolation.
- 17:55 Reprioritised builder-1: be-approve before be-spam-tune-2 (critical path: beat 4 + unblocks fe-revision-diff). Lead had let a side-fix jump the critical path.
- 17:55 Postgres demo-idea-db-1 crash 10:46:42 UTC: a backend process exited code 2 → postmaster killed all, reinitialized. Before: auth timeouts (10:21, 10:25), 'terminating connection due to administrator command' 10:35 (likely a test fixture DROP DATABASE ... FORCE / pg_terminate_backend), checkpoint write 73 s (I/O pressure). Root cause unconfirmed; load = 2 builders + 2 reviewers running pytest/dev servers on one container. reviewer-2 #12: flow passed before merge, shots in pr-shots/pr12 (body not edited).
- 18:00 INCIDENT: shared Postgres taken down by builder-3 running 'docker compose up -d --wait db' in a worktree without .env → DB_PORT default 5432 ≠ 5442 → compose recreated demo-idea-db-1 (stuck Created). Lead identified via process tree (cwd wt-ci-make-reseed), stopped builder-3, restored from main repo; named volume demo-idea_pgdata kept data. ~5 min outage; reviewer-1 pass 2 paused. Skill gap: builders need 'never touch docker/compose; shared infra is lead-owned' + worktrees need .env copied.
- 18:00 reviewer-1 diff flag on merged #13: reseed() uses create_all → fresh DB gets tables w/o alembic_version. Mitigated in ci-make-reseed (alembic upgrade head before reseed). Backend cleanup (drop create_all) left as nit.
- 18:01 #15 merged; reviewer saw make reseed ~20 s wall (reseed 4.4 s) vs builder 8 s → T4.3 (<10 s) at risk on cold uv/alembic start; recheck on demo host.
- 18:01 reviewer-2 #14 pre-merge flow OK (F3). Nits → fe-anim-polish (builder-2, idle otherwise). Link-only spam miss confirmed again → be-spam-tune-2.

### Paused 18:02 (start 16:49:05) · 14 PRs merged (#1, #3–#15; #2 closed) · open: 0

### Plugin feedback (issue → fix)
1. Lead has no TaskCreate/TaskUpdate in this runtime → skill must fall back to plan.md queue in prompts.
2. Builders can't SendMessage "team-lead" (lead is main session) → name the lead's real address in spawn prompt.
3. pr_poll.py only polls open PRs → MERGED never fires (patched: re-poll PRs last seen OPEN).
4. Reviewer exits after each review, push-only → slow; made self-polling 2-pass (fast diff ≤90 s, deep later) with labels.
5. Human merges in 30 s–7 min, faster than pre-review → define merge gate (label pre-review:ok) or skip review once merged (now rule).
6. One reviewer serial → add reviewer per folder, each with own ports/DBs/worktrees.
7. No visual check in reviewer → add screenshot step (UI) and Playwright flow (interactive), embed via pr-shots branch in PR body.
8. gh can't upload images → document pr-shots orphan branch + blob?raw=true pattern.
9. Contract file (openapi.json + schema.d.ts) not named in plan → planning step must name codegen outputs as the shared contract file.
10. New worktree per task lacks .env + node_modules → codegen/tests fail; copy .env, install deps, or reuse worktree.
11. Auto-mode classifier blocks cross-folder codegen and security-file removal; allow rules don't match "cd <wt> && ..." → note in preflight, run without auto mode or let human do it.
12. Builders touched shared infra (docker compose in worktree without .env recreated shared Postgres) → rule: builders never run docker/compose; infra is lead-owned.
13. Shared test DB contended by 4 agents → crashes/flaky pytest → per-agent TEST_DATABASE_URL.
14. Port collisions between agents (vite preview 4173) → assign ports per agent in spawn prompt.
15. Reviewer messaged two builders with competing fixes → reviewer reports to owner builder + lead only.
16. Lead relayed fix before reading human PR comments → watcher/lead must read PR comments first; one router (watcher) per PR.
17. Lead bundled 2 intents in one task (secret scan + reseed) → plan check: one intent, no dependency on unmerged code.
18. Vertical shape starved FE builder (serial backend chain) → plan FE work against a mock/contract first; prioritise critical path explicitly.
19. Lead let side fixes jump the critical path → plan.md needs a critical-path column; lead reorders on each merge.
20. CI never ran (Actions startup_failure, account billing) → preflight: confirm one workflow run succeeds; paths filter must include scripts/Makefile/.github.
21. Watcher reported stale budget from state.json → watcher recounts via gh before reporting.
22. Plugin cache (0.3.0) ignores edited agent files → document "update plugin after editing" or spawn with file path.
- 18:04 Paused state: be-approve pushed (b8edcf8, no PR, 7 tests); be-spam-tune-2 local only (9/9 spam, 1/10 real flagged); fe-anim-polish pushed (c5de20f, no PR). Not started: fe-revision-diff, be-llm-classifier.
- 10:00 Plugin PR opened from fork: https://github.com/bachtly/bach-workflow/pull/1 (commit 1 re-adds pr-team 06fc555, commit 2 pr_poll fix 09c8c55). Upstream repo appears recreated: PR numbering restarted at #1, PR #4 404, 8a90db1 unknown.

### Agent-team verification in terminal (2026-10-05)
- VS Code extension session = Agent SDK → `Agent(name=…)` runs as plain subagents (documented). Yesterday's run was named subagents, not a team.
- Terminal `claude` (wt-app-stack): real team created (`~/.claude/teams/session-545161a0`, lead `team-lead`, in-process). alice↔bob direct messages, bob → team-lead, idle then resumed by message, shutdown_request approved by both.
- guard-infra hook blocked teammate bob's `docker ps` ("Blocked by guard-infra … matched: docker").
- Task tools on Opus 5.5: off by default. `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` → TaskCreate/TaskList/TaskUpdate yes (deferred, load via ToolSearch). `CLAUDE_CODE_ENABLE_TASKS=1` → no.
- Lượt C (task list): lead TaskCreate ×2 + `addBlockedBy` OK. alice and bob self-claimed via TaskList/TaskUpdate (no direct assignment). **Race:** both claimed #1 in the same second (08:05:42), both ran it (idempotent here, so the file was still right). Blocking held: #2 only claimed after #1 completed (alice). Completed tasks vanish from TaskList ("No tasks found"); the task dir keeps only .lock/.highwatermark. → Claiming is not atomic; pr-team needs owner verification or lead-assigned owners / folder-scoped claims.
