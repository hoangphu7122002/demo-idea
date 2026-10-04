# Reference sources: AI + System Design (path: AI Solution Engineer)

Use: feature analysis and inspiration for the blog, not content copying.
Crawl rules: respect robots.txt, prefer RSS/sitemap, ≤1 req/s, store metadata + a few sample pages only.
SPA sites (Knowbie, explainers) need a real browser render (playwright-core, as in banhloc `tools/scrape`).
Bot-protected sites (Reddit, G2): read by hand, don't bypass.

What to record per site: format (post / course / interactive), interactive widget types, TOC, math, code,
diagrams, citations, series, comments, contribution model, freshness signal (date / updated / version),
search, newsletter, tech stack.

## Track 1 · AI (applied + deep research)

### Deep research
| Source | URL | Why |
|---|---|---|
| Lil'Log | lilianweng.github.io | Long survey posts, math, citations, TOC (Hugo PaperMod) |
| Distill | distill.pub | Interactive ML papers, open peer review |
| Chris Olah | colah.github.io | Visual intuition for deep learning |
| Transformer Circuits | transformer-circuits.pub | Interpretability research, interactive figures |
| Jay Alammar | jalammar.github.io | "Illustrated" step-by-step visuals |
| Andrej Karpathy | karpathy.github.io | Deep posts + from-scratch code |
| Sebastian Raschka · Ahead of AI | magazine.sebastianraschka.com | LLM research digests, newsletter |
| Hugging Face blog | huggingface.co/blog | Model/technique deep dives with code |

### Applied (AI engineering)
| Source | URL | Why |
|---|---|---|
| Chip Huyen | huyenchip.com | ML/AI systems in production |
| Eugene Yan | eugeneyan.com | LLM patterns, evals, RecSys |
| Hamel Husain | hamel.dev | Evals, fine-tuning in practice |
| Simon Willison | simonwillison.net | TIL style, fast updates, tags, cross-links |
| Anthropic Engineering | anthropic.com/engineering | Agents, tool use, context engineering |
| OpenAI Cookbook | cookbook.openai.com | Runnable recipes |
| Jason Liu | jxnl.co | RAG, structured outputs, consulting view |

### Interactive AI explainers
| Source | URL | Why |
|---|---|---|
| Knowbie | knowbie.vercel.app | Interactive deep-internals courses (SPA) |
| Transformer Explainer | poloclub.github.io/transformer-explainer | Live GPT-2 in browser |
| LLM Visualization | bbycroft.net/llm | 3D walkthrough of an LLM |
| TensorFlow Playground | playground.tensorflow.org | Train a small net interactively |
| CNN Explainer | poloclub.github.io/cnn-explainer | Layer-by-layer visual |

## Track 2 · System Design + Architecture

### Deep
| Source | URL | Why |
|---|---|---|
| Martin Kleppmann | martin.kleppmann.com | Distributed data (DDIA author) |
| Marc Brooker | brooker.co.za/blog | Distributed systems at AWS scale |
| AWS Builders' Library | aws.amazon.com/builders-library | Real-world reliability patterns |
| Jepsen | jepsen.io | Consistency analyses of real databases |
| Murat Demirbas | muratbuffalo.blogspot.com | Paper reviews, distributed systems |
| Martin Fowler | martinfowler.com | Architecture patterns, evolving articles (freshness model) |
| Dan Luu | danluu.com | Long data-driven essays |

### Applied / case studies
| Source | URL | Why |
|---|---|---|
| ByteByteGo (Alex Xu) | blog.bytebytego.com | System design with diagrams, newsletter |
| High Scalability | highscalability.com | Architecture case studies |
| Netflix / Uber / Discord engineering blogs | netflixtechblog.com, uber.com/blog/engineering, discord.com/blog | Production architecture write-ups |
| System Design Primer | github.com/donnemartin/system-design-primer | Community-contributed (PR model) |

### Interactive
| Source | URL | Why |
|---|---|---|
| Sam Who | samwho.dev | Animated load balancing, hashing, queues |
| The Secret Lives of Data (Raft) | thesecretlivesofdata.com/raft | Step-by-step consensus |
| VisuAlgo | visualgo.net | Algorithms/data structures step by step |
| Bartosz Ciechanowski | ciechanow.ski | Gold standard of in-post simulation |

## Bridge · AI Solution Engineer
| Source | URL | Why |
|---|---|---|
| Azure Architecture Center (AI) | learn.microsoft.com/azure/architecture | Reference architectures for AI apps |
| AWS Architecture Blog / ML blog | aws.amazon.com/blogs/architecture | Solution patterns, trade-offs |
| Google Cloud Architecture Center | cloud.google.com/architecture | GenAI reference designs |
| a16z · Emerging LLM app stack | a16z.com | Landscape of the LLM app stack |

## Vietnamese
| Source | URL | Why |
|---|---|---|
| Viblo | viblo.asia | VN dev community, comments, reputation |
| nvbinh | substack.com/@nvbinh | VN newsletter model |

## Community contribution / freshness models (for core A + B)
| Source | Model |
|---|---|
| MDN | Edit via GitHub, contributor credit |
| Stack Overflow | Suggested edits reviewed by reputation holders |
| Wikipedia | Revision history, talk pages, "needs update" banners |
| Martin Fowler | Articles revised over time with change notes |
| Hypothesis | Paragraph-level annotations |
