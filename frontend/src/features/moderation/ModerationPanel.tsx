import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { QueryState } from '../../components/QueryState'
import { useMutationToast } from '../../hooks/useMutationToast'
import { useGetSuggestionsQuery, useRunFilterMutation } from './moderationApi'
import { SuggestionCard } from './SuggestionCard'

/** Author side panel: Pending queue, Run filter, and the separate Filtered pile with its count. */
export function ModerationPanel({ slug }: { slug: string }) {
  const pending = useGetSuggestionsQuery({ slug, status: 'pending' })
  const filtered = useGetSuggestionsQuery({ slug, status: 'filtered' })
  const [runFilter, { isLoading: running }] = useRunFilterMutation()
  const run = useMutationToast()

  const onRun = () => run(runFilter(slug).unwrap(), { success: 'Filter finished', error: 'Could not run filter' })

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
          <QueryState query={pending} emptyMessage="No pending suggestions.">
            {(items) => items.map((s) => <SuggestionCard key={s.id} suggestion={s} onApprove={() => {}} approveDisabled />)}
          </QueryState>
        </Stack>

        <Stack spacing={1} data-testid="filtered-list">
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Typography variant="subtitle2">Filtered</Typography>
            <Chip label={filtered.data?.length ?? 0} color="warning" data-testid="filtered-count" />
          </Stack>
          <QueryState query={filtered} emptyMessage="Nothing filtered.">
            {(items) => items.map((s) => <SuggestionCard key={s.id} suggestion={s} />)}
          </QueryState>
        </Stack>
      </Stack>
    </Box>
  )
}
