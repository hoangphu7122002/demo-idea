import type { Root, Nodes } from 'mdast'
import { visit } from 'unist-util-visit'

const ANCHORED = new Set(['paragraph', 'heading', 'code', 'math', 'inlineMath', 'inlineCode', 'blockquote', 'listItem', 'table'])

/** Writes `data-src-start` / `data-src-end` (source offsets in the MDX) onto each block and inline-code/math element. */
export function remarkSourcePos() {
  return (tree: Root) => {
    visit(tree, (node: Nodes) => {
      const pos = node.position
      if (!ANCHORED.has(node.type) || !pos) return
      const data = (node.data ??= {}) as { hProperties?: Record<string, unknown> }
      data.hProperties = {
        ...data.hProperties,
        'data-src-start': pos.start.offset,
        'data-src-end': pos.end.offset,
      }
    })
  }
}
