import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { QueryState } from '../../components/QueryState'
import { useMutationToast } from '../../hooks/useMutationToast'
import { useState } from 'react'
import type { Suggestion } from '../suggest/suggestApi'
import { FilteredList } from './FilteredList'
import { moveTotalMs, MOVE_MS, slideOut, STAGGER_MS } from './moveAnim'
import { useCountUp } from './useCountUp'
import { useApproveSuggestionMutation, useGetSuggestionsQuery, useRunFilterMutation } from './moderationApi'
import { SuggestionCard } from './SuggestionCard'

/** Author side panel: Pending queue, Run filter, and the separate Filtered pile with its count. */
export function ModerationPanel({ slug }: { slug: string }) {
  const pending = useGetSuggestionsQuery({ slug, status: 'pending' })
  const filtered = useGetSuggestionsQuery({ slug, status: 'filtered' })
  const [runFilter, { isLoading: running }] = useRunFilterMutation()
  const [approve] = useApproveSuggestionMutation()
  const run = useMutationToast()

  // Items caught by a run: they linger in Pending while sliding out, then show up in Filtered, staggered.
  const [leaving, setLeaving] = useState<Suggestion[]>([])
  const [entering, setEntering] = useState<Record<number, number>>({})
  const [blocked, startBlockedFrom] = useCountUp(filtered.data?.length ?? 0)

  const onRun = async () => {
    const before = pending.data ?? []
    startBlockedFrom(filtered.data?.length ?? 0)
    const ok = await run(runFilter(slug).unwrap(), { success: 'Filter finished', error: 'Could not run filter' })
    if (!ok) return
    const after = await Promise.all([pending.refetch().unwrap(), filtered.refetch().unwrap()])
    const filteredIds = new Set(after[1].map((x) => x.id))
    const moved = before.filter((x) => filteredIds.has(x.id))
    setLeaving(moved)
    setEntering(Object.fromEntries(moved.map((x, i) => [x.id, i])))
    setTimeout(() => {
      setLeaving([])
      setEntering({})
    }, moveTotalMs(moved.length))
  }

  return (
    <Box component="aside" aria-label="Moderation" data-testid="moderation-panel" sx={{ width: 320, flexShrink: 0, display: { xs: 'none', md: 'block' } }}>
      <Stack spacing={2} sx={{ position: 'sticky', top: 16, fontFamily: 'Inter, system-ui, sans-serif' }}>
        <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Moderation</Typography>
          <Button variant="outlined" size="small" loading={running} onClick={onRun} data-testid="run-filter">
            Run filter
          </Button>
        </Stack>

        <Stack spacing={1} data-testid="pending-list">
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Typography variant="subtitle2">Pending</Typography>
            <Chip label={pending.data?.length ?? 0} data-testid="pending-count" />
          </Stack>
          {leaving.map((s, i) => (
            <Box key={s.id} data-moving="true" sx={{ overflow: 'hidden', animation: `${slideOut} ${MOVE_MS}ms ease-in both`, animationDelay: `${i * STAGGER_MS}ms` }}>
              <SuggestionCard suggestion={s} />
            </Box>
          ))}
          <QueryState query={pending} emptyMessage="No pending suggestions.">
            {(items) => items.map((s) => <SuggestionCard key={s.id} suggestion={s} onApprove={(x) => run(approve(x.id).unwrap(), { success: 'Approved', error: 'Could not approve' })} />)}
          </QueryState>
        </Stack>

        <FilteredList query={filtered} entering={entering} blocked={blocked} />
      </Stack>
    </Box>
  )
}
