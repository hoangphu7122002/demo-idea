import Chip from '@mui/material/Chip'
import { creditLabel } from './revisionMeta'

export function CreditBadge({ name }: { name?: string | null }) {
  return <Chip size="small" color="success" variant="outlined" label={creditLabel(name)} data-testid="credit-badge" sx={{ ml: 0.5, verticalAlign: 'middle', fontFamily: 'Inter, system-ui, sans-serif' }} />
}
