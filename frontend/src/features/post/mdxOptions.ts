import rehypeShikiFromHighlighter from '@shikijs/rehype/core'
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import { createHighlighterCore } from 'shiki/core'
import { createJavaScriptRegexEngine } from 'shiki/engine/javascript'
import { rehypeCollectPrePos, rehypeRestorePrePos } from './rehypeKeepPrePos.ts'
import { remarkSourcePos } from './remarkSourcePos.ts'

// Fine-grained bundle: only the languages posts use (keeps the build small, no 430 grammar assets).
const highlighter = await createHighlighterCore({
  themes: [import('@shikijs/themes/github-light'), import('@shikijs/themes/github-dark')],
  langs: [
    import('@shikijs/langs/typescript'),
    import('@shikijs/langs/javascript'),
    import('@shikijs/langs/python'),
    import('@shikijs/langs/bash'),
    import('@shikijs/langs/json'),
  ],
  engine: createJavaScriptRegexEngine(),
})

/** Shared by the Vite build-time plugin (fixtures) and runtime `evaluate` (posts from the API). */
export const mdxOptions = {
  remarkPlugins: [remarkMath, remarkSourcePos],
  rehypePlugins: [
    rehypeKatex,
    rehypeCollectPrePos,
    [rehypeShikiFromHighlighter, highlighter, { themes: { light: 'github-light', dark: 'github-dark' }, defaultColor: 'light', fallbackLanguage: 'text' }],
    rehypeRestorePrePos,
  ],
} as never
