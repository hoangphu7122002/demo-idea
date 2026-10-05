import { useEffect, useState, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { CreditBadge } from './CreditBadge'
import { InlineDiff } from './InlineDiff'
import { plainMd, unescapeMdx, type SpanRevision } from './revisionMeta'

interface Props {
  containerRef: RefObject<HTMLElement | null>
  source: string
  revision: SpanRevision
  showChanges: boolean
}

interface Marks {
  host: HTMLElement
  diffHost: HTMLElement
  badgeHost: HTMLElement
}

function setHidden(el: HTMLElement, hidden: boolean) {
  el.hidden = hidden
}

/** Deepest anchored block whose source range holds `pos`. */
function findBlock(root: HTMLElement, pos: number): HTMLElement | null {
  let best: HTMLElement | null = null
  let bestLen = Infinity
  root.querySelectorAll<HTMLElement>('[data-src-start]').forEach((el) => {
    const s = Number(el.dataset.srcStart)
    const e = Number(el.dataset.srcEnd)
    if (s <= pos && pos < e && e - s < bestLen) {
      best = el
      bestLen = e - s
    }
  })
  return best
}

function textNodes(block: HTMLElement): Text[] {
  const w = document.createTreeWalker(block, NodeFilter.SHOW_TEXT)
  const out: Text[] = []
  for (let n = w.nextNode(); n; n = w.nextNode()) out.push(n as Text)
  return out
}

/** Range over `needle` inside the block's text, or the whole block content when it is not found. */
function countOf(hay: string, needle: string): number {
  let n = 0
  for (let i = hay.indexOf(needle); i >= 0 && needle; i = hay.indexOf(needle, i + needle.length)) n++
  return n
}

/** Nth occurrence start (0-based) of needle in hay, else the first, else -1. */
function nthIndex(hay: string, needle: string, n: number): number {
  let at = -1
  for (let k = 0; k <= n; k++) {
    at = hay.indexOf(needle, at < 0 ? 0 : at + needle.length)
    if (at < 0) return hay.indexOf(needle)
  }
  return at
}

function locate(block: HTMLElement, needles: { text: string; nth: number }[]): Range {
  const nodes = textNodes(block)
  const full = nodes.map((n) => n.data).join('')
  const range = document.createRange()
  for (const { text: needle, nth } of needles) {
    const at = needle ? nthIndex(full, needle, nth) : -1
    if (at < 0) continue
    const pos = (offset: number) => {
      let acc = 0
      for (const n of nodes) {
        if (offset <= acc + n.data.length) return { node: n, off: offset - acc }
        acc += n.data.length
      }
      return { node: nodes[nodes.length - 1], off: nodes[nodes.length - 1].data.length }
    }
    const a = pos(at)
    const b = pos(at + needle.length)
    range.setStart(a.node, a.off)
    range.setEnd(b.node, b.off)
    return range
  }
  range.selectNodeContents(block)
  return range
}

/**
 * Marks the latest credited change inside the rendered post: a "fixed by" badge always, the inline diff on demand.
 * The span is looked up only inside the block that owns its source offset, so repeated text elsewhere is ignored.
 */
export function RevisionLayer({ containerRef, source, revision, showChanges }: Props) {
  const [marks, setMarks] = useState<Marks | null>(null)
  const newText = source.slice(revision.change_start, revision.change_end)

  useEffect(() => {
    const root = containerRef.current
    if (!root) return
    let host: HTMLElement | null = null
    let badgeHost: HTMLElement | null = null
    let diffHost: HTMLElement | null = null
    const attempt = () => {
      const block = findBlock(root, revision.change_start)
      if (!block || !textNodes(block).length) return false
      const prefix = source.slice(Number(block.dataset.srcStart), revision.change_start)
      const range = locate(
        block,
        [unescapeMdx, plainMd].map((f) => ({ text: f(newText), nth: countOf(f(prefix), f(newText)) })),
      )
      host = document.createElement('span')
      host.dataset.revisionSpan = 'true'
      host.append(range.extractContents())
      range.insertNode(host)
      diffHost = document.createElement('span')
      diffHost.hidden = true
      badgeHost = document.createElement('span')
      host.after(diffHost, badgeHost)
      setMarks({ host, diffHost, badgeHost })
      return true
    }
    let obs: MutationObserver | null = null
    if (!attempt()) {
      // MDX compiles async; wait for the blocks to appear.
      obs = new MutationObserver(() => {
        if (attempt()) obs?.disconnect()
      })
      obs.observe(root, { childList: true, subtree: true })
    }
    return () => {
      obs?.disconnect()
      diffHost?.remove()
      badgeHost?.remove()
      host?.replaceWith(...Array.from(host.childNodes))
      setMarks(null)
    }
  }, [containerRef, source, revision.change_start, newText])

  useEffect(() => {
    if (!marks) return
    setHidden(marks.host, showChanges)
    setHidden(marks.diffHost, !showChanges)
  }, [marks, showChanges])

  if (!marks) return null
  return (
    <>
      {showChanges && createPortal(<InlineDiff oldText={revision.previous_text ?? ''} newText={unescapeMdx(newText)} />, marks.diffHost)}
      {createPortal(<CreditBadge name={revision.credit_name} />, marks.badgeHost)}
    </>
  )
}
