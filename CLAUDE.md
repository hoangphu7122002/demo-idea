# Repo rules

## Opening PRs

GitHub Actions is unreliable, so test evidence is generated locally and lives in the PR body.

- Open PRs only via `scripts/pr-open.sh [--title ... --body ...]` (wraps `gh pr create`). It runs only the suites for the paths you changed (backend/ and/or frontend/), diffs tests against main, takes before/after screenshots for changed frontend routes (`SHOT_ROUTES="/notes,/chat"` to override), and writes it all between `<!-- evidence:start -->` / `<!-- evidence:end -->` in the body.
- After pushing more commits: `scripts/pr-open.sh --update <n>`.
- Pieces if needed: `scripts/test-report.sh [base]` (or `make report`), `scripts/ui-shots.sh [base]`; output in `.test-report/` (gitignored).
- Requires `docker compose up -d db redis` (`make check` does it).

## Reviewers

Block the PR if the body has no evidence block, the evidence is stale (head SHA not the PR head), or "Newly failing" is non-zero.
