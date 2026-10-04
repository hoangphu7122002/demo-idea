import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import type { Suggestion } from '../suggest/suggestApi'

interface Props {
  suggestion: Suggestion
  /** Approve is shown on pending items only; it stays disabled until the approve endpoint exists. */
  onApprove?: (s: Suggestion) => void
  approveDisabled?: boolean
}

export function SuggestionCard({ suggestion: s, onApprove, approveDisabled }: Props) {
  return (
    <Box data-testid={`suggestion-${s.id}`} sx={{ p: 1.5, border: 1, borderColor: 'divider', borderRadius: 1 }}>
      <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }} data-testid="suggestion-original">
        “{s.original_text}”
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600, my: 0.5 }} data-testid="suggestion-replacement">
        {s.replacement}
      </Typography>
      <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="caption" color="text.secondary" data-testid="suggestion-name">
          {s.name?.trim() || 'a reader'}
        </Typography>
        {onApprove && (
          <Button size="small" variant="contained" disabled={approveDisabled} onClick={() => onApprove(s)} data-testid={`approve-${s.id}`}>
            Approve
          </Button>
        )}
      </Stack>
    </Box>
  )
}
