# Decision — 2026-10-04
Rule (rules/gates.md): G1 partial, G2 pass, G3 partial, G4 pass → NARROW.
Critic: NOT YET (push-back held, critic_discarded=false). Kill-shot: demo pain (stale posts readers can't fix) has no recent evidence.
User decision: NARROW (pending: narrow direction). Code freeze: TBD. Stack: TBD ("cần interactive" — clarify).
Interview round 1: persona=dev personal blog; trigger=reader finds error/stale post; output=new revision + credit; constraints=EN/VI, non-GitHub login, no-ops moderation, local demo.
Narrow: option 1 (moderation/spam pain).

## Re-decide after NARROW (wf_65b4d0cd-2bc)
G1 FAIL (spam theme: 4 paraphrased rows, only E331 on-theme) · G2 pass · G3 partial · G4 partial.
Critic: NO-GO; push-back held (critic_discarded=false). Rule: G1 fail → KILL.
Interview round 2: today=giscus GitHub-only login; look=Medium inline highlight; "interactive" = posts with interactive examples like knowbie; spam filter = rules + LLM.

## FINAL: GO (user override, 2026-10-04)
Against rule (G1 fail → KILL) and critic NO-GO. User accepts risk: pain evidence unproven; purpose = hackathon demo.
Scope direction: MDX+React blog base (seeded, Knowbie-style look, 1 lab) + anonymous inline suggestion → rules+LLM spam filter → author approve → revision + credit. Voice/video v2.
Core job: A dev blogger lets any reader (anonymous, no login) suggest fixes inline without spam cleanup or Git PRs.
Stack: lean-web-stack in /Users/hoangphu/demo-idea (Vite React + MDX, FastAPI, Postgres, PydanticAI). Code freeze: day 2 16:00.
