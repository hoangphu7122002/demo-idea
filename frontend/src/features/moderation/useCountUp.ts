import { useEffect, useState } from 'react'
import { STAGGER_MS } from './moveAnim'

/**
 * Returns `target`, except that after `startFrom(n)` is called the value climbs from n to target one step per stagger tick.
 * Used so the "N spam blocked" counter ticks up in sync with items landing in the Filtered list.
 */
export function useCountUp(target: number) {
  const [from, setFrom] = useState<number | null>(null)
  const shown = from === null ? target : Math.min(from, target)
  useEffect(() => {
    if (from === null) return
    if (from >= target) return
    const t = setTimeout(() => setFrom(from + 1), STAGGER_MS)
    return () => clearTimeout(t)
  }, [from, target])
  return [shown, setFrom] as const
}
