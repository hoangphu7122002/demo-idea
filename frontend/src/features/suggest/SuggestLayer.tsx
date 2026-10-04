import { useEffect, useState, type RefObject } from 'react'
import { anchorFromRange, type SuggestionAnchor } from './anchor'
import { SuggestPopup } from './SuggestPopup'


interface Props {
  slug: string
  /** The article element whose text can be selected. */
  containerRef: RefObject<HTMLElement | null>
  /** MDX source the rendered text came from; enables span-level anchors. */
  source: string | null
}

/** Listens for text selection inside the post and opens the suggestion popup next to it. */
export function SuggestLayer({ slug, containerRef, source }: Props) {
  const [anchor, setAnchor] = useState<SuggestionAnchor | null>(null)

  useEffect(() => {
    const root = containerRef.current
    if (!root) return
    const open = () => {
      const sel = window.getSelection()
      if (!sel || sel.isCollapsed || sel.rangeCount === 0) return
      const next = anchorFromRange(sel.getRangeAt(0), root, source)
      if (next) setAnchor(next)
    }
    const close = () => setAnchor(null)
    root.addEventListener('mouseup', open)
    root.addEventListener('keyup', open)
    root.addEventListener('mousedown', close)
    return () => {
      root.removeEventListener('mouseup', open)
      root.removeEventListener('keyup', open)
      root.removeEventListener('mousedown', close)
    }
  }, [containerRef, source])

  if (!anchor) return null
  return <SuggestPopup key={`${anchor.paragraph_id}:${anchor.original_text}`} slug={slug} anchor={anchor} onClose={() => setAnchor(null)} />
}
