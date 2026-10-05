import type { components } from '../../api/schema'

export type Revision = components['schemas']['RevisionOut']

/** A revision that carries a credited change span (offsets into the current source). */
export interface SpanRevision extends Revision {
  change_start: number
  change_end: number
}

export function creditLabel(name?: string | null): string {
  return `fixed by ${name?.trim() || 'a reader'}`
}

/** Latest revision with a change span; older spans are stale against the current source. */
export function latestSpanRevision(revisions: Revision[] | undefined): SpanRevision | null {
  const last = revisions?.[revisions.length - 1]
  if (last && last.change_start != null && last.change_end != null) return last as SpanRevision
  return null
}

/** The stored span is MDX-escaped in prose; rendered text has no backslashes before these. */
export function unescapeMdx(s: string): string {
  return s.replace(/\\([{}<>])/g, '$1')
}

/** Strip inline markdown markers so a span like `**x**` can match rendered text. */
export function plainMd(s: string): string {
  return unescapeMdx(s).replace(/[*_`~]/g, '')
}
