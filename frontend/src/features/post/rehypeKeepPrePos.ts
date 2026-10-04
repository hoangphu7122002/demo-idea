import type { Element, Root } from 'hast'
import type { VFile } from 'vfile'
import { visit } from 'unist-util-visit'

const SRC = ['data-src-start', 'data-src-end'] as const

/** remark-rehype puts the code node's data on `<code>`, and Shiki then replaces `<pre>` and drops it. `collect` runs before Shiki, `restore` after, matched by document order. */
export function rehypeCollectPrePos() {
  return (tree: Root, file: VFile) => {
    const found: Element['properties'][] = []
    visit(tree, 'element', (el: Element) => {
      if (el.tagName === 'pre') {
        const code = el.children.find((c): c is Element => c.type === 'element' && c.tagName === 'code')
        found.push(Object.fromEntries(SRC.map((k) => [k, code?.properties[k]])))
      }
    })
    file.data.prePos = found
  }
}

export function rehypeRestorePrePos() {
  return (tree: Root, file: VFile) => {
    const found = (file.data.prePos as Element['properties'][] | undefined) ?? []
    let i = 0
    visit(tree, 'element', (el: Element) => {
      if (el.tagName === 'pre') Object.assign(el.properties, found[i++])
    })
  }
}
