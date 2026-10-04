import Chip from '@mui/material/Chip'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { QueryState } from '../../components/QueryState'
import { MOVE_MS, slideIn, STAGGER_MS } from './moveAnim'
import { SuggestionCard } from './SuggestionCard'
import type { Suggestion } from '../suggest/suggestApi'

interface Props {
  query: Parameters<typeof QueryState<Suggestion[]>>[0]['query']
  /** Items that just arrived from a filter run, keyed by id to their stagger index. */
  entering: Record<number, number>
  /** Live "N spam blocked" figure, counted up as items land. */
  blocked: number
}

export function FilteredList({ query, entering, blocked }: Props) {
  return (
    <Stack spacing={1} data-testid="filtered-list">
      <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
        <Typography variant="subtitle2">Filtered</Typography>
        <Chip label={query.data?.length ?? 0} color="warning" data-testid="filtered-count" />
        <Chip label={`${blocked} spam blocked`} color="error" variant="outlined" data-testid="spam-blocked" />
      </Stack>
      <QueryState query={query} emptyMessage="Nothing filtered.">
        {(items) =>
          items.map((s) =>
            s.id in entering ? (
              <Stack
                key={s.id}
                data-moving="true"
                sx={{ animation: `${slideIn} ${MOVE_MS}ms ease-out both`, animationDelay: `${entering[s.id] * STAGGER_MS}ms` }}
              >
                <SuggestionCard suggestion={s} />
              </Stack>
            ) : (
              <SuggestionCard key={s.id} suggestion={s} />
            ),
          )
        }
      </QueryState>
    </Stack>
  )
}
