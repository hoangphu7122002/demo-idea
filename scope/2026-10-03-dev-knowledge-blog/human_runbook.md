# Your research tasks (about 40 minutes, while the agents run)

Agents cannot open these sites (403 / login walls). Paste what you find into
`evidence_human.csv` in this folder, one row per quote. Columns:

| Column | Value |
|---|---|
| type | `pain` (a complaint), `review` (competitor 1–3★ review), `competitor` (a tool you found), `spend` (someone paying for it) |
| source | e.g. `reddit r/freelance`, `G2 <competitor>`, `Capterra <competitor>` |
| url | link to the post or review |
| date | YYYY-MM-DD (approx is fine) |
| quote_or_number | the exact words, copy-pasted |
| persona_match | `y` if the writer matches the persona, else `n` |
| theme | 2–4 word tag, e.g. `chasing payment`, `too complex` (optional) |
| note | anything else |

## H1 · Reddit (20 min)
Open each link, set **Sort: Top · Time: Past year** if not already, open the
10 longest threads, copy the most specific complaints. Long rants with details
count most.

Focus: themes for core **A + B**: feedback/corrections that never reach the post (A), outdated posts (B). Aim for **≥10 quotes from ≥3 subreddits** on one theme.

- [blog comments useless · all](https://www.reddit.com/search/?q=blog+comments+useless&sort=top&t=year)
- [readers correct my blog post · all](https://www.reddit.com/search/?q=readers+correct+my+blog+post&sort=top&t=year)
- [suggest edit blog post · all](https://www.reddit.com/search/?q=suggest+edit+blog+post&sort=top&t=year)
- [outdated tutorial wasted hours · all](https://www.reddit.com/search/?q=outdated+tutorial+wasted+hours&sort=top&t=year)
- [blog post no longer works · all](https://www.reddit.com/search/?q=blog+post+no+longer+works&sort=top&t=year)
- [why I stopped blogging · all](https://www.reddit.com/search/?q=why+I+stopped+blogging&sort=top&t=year)
- [r/webdev · blog comments useless](https://www.reddit.com/r/webdev/search/?q=blog+comments+useless&restrict_sr=1&sort=top&t=year)
- [r/webdev · readers correct my blog post](https://www.reddit.com/r/webdev/search/?q=readers+correct+my+blog+post&restrict_sr=1&sort=top&t=year)
- [r/webdev · suggest edit blog post](https://www.reddit.com/r/webdev/search/?q=suggest+edit+blog+post&restrict_sr=1&sort=top&t=year)
- [r/webdev · outdated tutorial wasted hours](https://www.reddit.com/r/webdev/search/?q=outdated+tutorial+wasted+hours&restrict_sr=1&sort=top&t=year)
- [r/webdev · blog post no longer works](https://www.reddit.com/r/webdev/search/?q=blog+post+no+longer+works&restrict_sr=1&sort=top&t=year)
- [r/programming · blog comments useless](https://www.reddit.com/r/programming/search/?q=blog+comments+useless&restrict_sr=1&sort=top&t=year)
- [r/programming · readers correct my blog post](https://www.reddit.com/r/programming/search/?q=readers+correct+my+blog+post&restrict_sr=1&sort=top&t=year)
- [r/programming · suggest edit blog post](https://www.reddit.com/r/programming/search/?q=suggest+edit+blog+post&restrict_sr=1&sort=top&t=year)
- [r/programming · outdated tutorial wasted hours](https://www.reddit.com/r/programming/search/?q=outdated+tutorial+wasted+hours&restrict_sr=1&sort=top&t=year)
- [r/programming · blog post no longer works](https://www.reddit.com/r/programming/search/?q=blog+post+no+longer+works&restrict_sr=1&sort=top&t=year)
- [r/ExperiencedDevs · blog comments useless](https://www.reddit.com/r/ExperiencedDevs/search/?q=blog+comments+useless&restrict_sr=1&sort=top&t=year)
- [r/ExperiencedDevs · readers correct my blog post](https://www.reddit.com/r/ExperiencedDevs/search/?q=readers+correct+my+blog+post&restrict_sr=1&sort=top&t=year)
- [r/ExperiencedDevs · suggest edit blog post](https://www.reddit.com/r/ExperiencedDevs/search/?q=suggest+edit+blog+post&restrict_sr=1&sort=top&t=year)
- [r/ExperiencedDevs · outdated tutorial wasted hours](https://www.reddit.com/r/ExperiencedDevs/search/?q=outdated+tutorial+wasted+hours&restrict_sr=1&sort=top&t=year)
- [r/ExperiencedDevs · blog post no longer works](https://www.reddit.com/r/ExperiencedDevs/search/?q=blog+post+no+longer+works&restrict_sr=1&sort=top&t=year)
- [r/blogging · blog comments useless](https://www.reddit.com/r/blogging/search/?q=blog+comments+useless&restrict_sr=1&sort=top&t=year)
- [r/blogging · readers correct my blog post](https://www.reddit.com/r/blogging/search/?q=readers+correct+my+blog+post&restrict_sr=1&sort=top&t=year)
- [r/blogging · suggest edit blog post](https://www.reddit.com/r/blogging/search/?q=suggest+edit+blog+post&restrict_sr=1&sort=top&t=year)
- [r/blogging · outdated tutorial wasted hours](https://www.reddit.com/r/blogging/search/?q=outdated+tutorial+wasted+hours&restrict_sr=1&sort=top&t=year)
- [r/blogging · blog post no longer works](https://www.reddit.com/r/blogging/search/?q=blog+post+no+longer+works&restrict_sr=1&sort=top&t=year)
- [r/selfhosted · blog comments useless](https://www.reddit.com/r/selfhosted/search/?q=blog+comments+useless&restrict_sr=1&sort=top&t=year)
- [r/selfhosted · readers correct my blog post](https://www.reddit.com/r/selfhosted/search/?q=readers+correct+my+blog+post&restrict_sr=1&sort=top&t=year)
- [r/selfhosted · suggest edit blog post](https://www.reddit.com/r/selfhosted/search/?q=suggest+edit+blog+post&restrict_sr=1&sort=top&t=year)
- [r/selfhosted · outdated tutorial wasted hours](https://www.reddit.com/r/selfhosted/search/?q=outdated+tutorial+wasted+hours&restrict_sr=1&sort=top&t=year)
- [r/selfhosted · blog post no longer works](https://www.reddit.com/r/selfhosted/search/?q=blog+post+no+longer+works&restrict_sr=1&sort=top&t=year)

## H4 · G2 / Capterra 1–3★ reviews (20 min)
For each competitor: open reviews, filter to 1–3 stars, read 10, copy each
complaint and tag a theme (price, missing feature, too complex, support, …).

Focus: complaints about comments, moderation, spam, contributions, outdated content (not billing/support).

- Ghost: [G2](https://www.g2.com/search?query=Ghost) · [Capterra](https://www.capterra.com/search/?query=Ghost)
- Hashnode: [G2](https://www.g2.com/search?query=Hashnode) · [Capterra](https://www.capterra.com/search/?query=Hashnode)
- WordPress: [G2](https://www.g2.com/search?query=WordPress) · [Capterra](https://www.capterra.com/search/?query=WordPress)
- Substack: [G2](https://www.g2.com/search?query=Substack) · [Capterra](https://www.capterra.com/search/?query=Substack)
- Disqus: [G2](https://www.g2.com/search?query=Disqus) · [Capterra](https://www.capterra.com/search/?query=Disqus)
- Hyvor Talk: [G2](https://www.g2.com/search?query=Hyvor+Talk) · [Capterra](https://www.capterra.com/search/?query=Hyvor+Talk)

When done, reply **done** in the Claude session.
