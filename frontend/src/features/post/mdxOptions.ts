import rehypeShiki from '@shikijs/rehype'
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import { rehypeCollectPrePos, rehypeRestorePrePos } from './rehypeKeepPrePos.ts'
import { remarkSourcePos } from './remarkSourcePos.ts'

/** Shared by the Vite build-time plugin (fixtures) and runtime `evaluate` (posts from the API). */
export const mdxOptions = {
  remarkPlugins: [remarkMath, remarkSourcePos],
  rehypePlugins: [
    rehypeKatex,
    rehypeCollectPrePos,
    [rehypeShiki, { themes: { light: 'github-light', dark: 'github-dark' }, defaultColor: 'light' }],
    rehypeRestorePrePos,
  ],
} as never
