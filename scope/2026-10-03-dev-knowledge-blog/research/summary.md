# Research summary: dev knowledge blog (Oct 2026; ~25 sources, 3 CSVs alongside)

## Verified problems
- Stop writing: fear of errors, no audience, regularity pressure ([buttondown](https://buttondown.com/jemmaissroff/archive/what-stops-people-from-writing), [jonbeckett](https://tiny.write.as/jonbeckett/why-i-dont-write-a-technical-blog-any-more)). Older sources (2019-21) partly; still consistent.
- Comments: spam + moderation burden, many authors turn off ([wiegman](https://chriswiegman.com/2021/10/blog-comments-are-hard/), older).
- Stale: blog = write-once, only date as signal; 32% outdated refs in one case ([dasroot](https://dasroot.net/posts/2026/04/technical-debt-management-long-running-blogs/), [techwhirl](https://techwhirl.com/users-advocate-get-rid-of-the-rot/)).
- Commons decay: SO questions -75% since 2014 ([tianpan](https://tianpan.co/forum/t/stack-overflow-questions-hit-near-zero-3-862-in-december-where-does-developer-knowledge-go-when-the-commons-dies/596)).

## Gaps nobody covers well
1. Feedback -> post improvement. Comments sit below post; fixes need Git PR ([wisp](https://www.wisp.blog/blog/medium-alternatives-developers)); giscus/utterances need GitHub login ([merginit](https://merginit.com/blog/21062026-free-commenting-platforms-comparison)). No tool turns a comment into a reviewed, credited edit of the post.
2. Per-claim/per-version freshness. Only dates; doc teams use manual last-reviewed metadata ([gitlab](https://gitlab.com/gitlab-com/gl-infra/observability/team/-/issues/4016)). Nothing reader-facing for blogs (e.g. "still valid on v X", reader-verified).
3. Contributor credit. Edit-this-page = PR, no reputation ([evefrontier](https://docs.evefrontier.com/contributing/contributing)); hosted platforms give only likes/followers.
4. Moderation without ops. Choice = GitHub-only, spam-prone (Cusdis/Isso), self-host Remark42, or paid ([merginit](https://merginit.com/blog/21062026-free-commenting-platforms-comparison), [pistack](https://www.pistack.xyz/posts/giscus-vs-remark42-vs-isso-self-hosted-comment-systems-guide-2026/)).
5. Voice -> structured technical post (code, math, series). Dictation tools = text only ([wispr](https://eesel.ai/blog/wispr-flow-overview), [superwhisper](https://apps.apple.com/il/app/id6471464415)); Voicenotes drafts generic posts ([mighil](https://mighil.com/this-blog-post-was-initially-drafted-on-voicenotescom)).
6. Post -> video integrated in publishing. Remotion+Claude Code works but needs code skill, slow render ([openreplay](https://blog.openreplay.com/making-videos-claude-code-remotion/)); not wired to blog.
7. Platform trust: Hashnode neglect/paywalling ([typeflo](https://typeflo.io/blog/hashnode-alternatives)); Medium no code/search ([wisp](https://www.wisp.blog/blog/medium-alternatives-developers)).

## Candidate differentiators (technical, not CRUD)
- A: Suggest-edit on selected text -> author accept/reject -> post revision + auto contributor credit (gaps 1,3,4). Best fit.
- B: Freshness engine: claims tied to versions; reader confirms/disputes; staleness badge (gap 2).
- C: Voice -> structured post (needs LLM pipeline; high demo risk) (gap 5).
- D: Post -> video (heavy render; v2) (gap 6).

## Caveats
- Hypothesis dev-blog usage: little evidence found. Reputation demand is inference. Several sources are vendor/listicle blogs; 2 comment-spam sources predate 24 months.
