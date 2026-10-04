export interface SuggestionAnchor {
  original_text: string
  anchor_start: number | null
  anchor_end: number | null
  paragraph_id: string | null
  /** 'span' = exact source range known; 'paragraph' = block-level only (code, math, ambiguous text). */
  level: 'span' | 'paragraph'
  rect: DOMRect
}

const blockOf = (node: Node | null): HTMLElement | null => {
  const el = node instanceof HTMLElement ? node : (node?.parentElement ?? null)
  return el?.closest<HTMLElement>('[data-src-start]') ?? null
}

/** Outermost anchored block (paragraph, heading, code, math display) that contains the node. */
const topBlock = (node: Node | null, root: HTMLElement): HTMLElement | null => {
  let block = blockOf(node)
  while (block) {
    const parent = block.parentElement ? blockOf(block.parentElement) : null
    if (!parent || !root.contains(parent)) break
    // Inline code/math inside a paragraph resolve to the paragraph; keep climbing.
    block = parent
  }
  return block && root.contains(block) ? block : null
}

/** Code blocks and KaTeX math get paragraph-level suggestions, not spans. */
const isRich = (block: HTMLElement, range: Range) => {
  const start = range.commonAncestorContainer
  const el = start instanceof HTMLElement ? start : start.parentElement
  return !!block.closest('pre') || !!el?.closest('.katex') || range.cloneContents().querySelector('.katex, pre') !== null
}

/**
 * Maps a DOM selection to a suggestion anchor. Prose gets a span (source offsets found inside the block's
 * source range); code blocks, KaTeX and ambiguous matches fall back to the paragraph id `start-end`.
 */
export function anchorFromRange(range: Range, root: HTMLElement, source: string | null): SuggestionAnchor | null {
  const text = range.toString().trim()
  if (!text) return null
  const block = topBlock(range.commonAncestorContainer, root)
  if (!block) return null
  const start = Number(block.dataset.srcStart)
  const end = Number(block.dataset.srcEnd)
  if (!Number.isFinite(start) || !Number.isFinite(end)) return null
  const base = { original_text: text, paragraph_id: `${start}-${end}`, rect: range.getBoundingClientRect() }
  if (source && !isRich(block, range)) {
    const inBlock = source.slice(start, end)
    const at = inBlock.indexOf(text)
    if (at >= 0 && inBlock.indexOf(text, at + 1) < 0) {
      return { ...base, anchor_start: start + at, anchor_end: start + at + text.length, level: 'span' }
    }
  }
  return { ...base, anchor_start: null, anchor_end: null, level: 'paragraph' }
}
