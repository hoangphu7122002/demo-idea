import Box from '@mui/material/Box'
import { diffWords } from 'diff'

/** Word diff: old words struck through, new words highlighted, shared words plain. */
export function InlineDiff({ oldText, newText }: { oldText: string; newText: string }) {
  const parts = diffWords(oldText, newText)
  return (
    <span data-testid="inline-diff">
      {parts.map((p, i) =>
        p.removed ? (
          <Box key={i} component="del" sx={{ color: 'error.main', textDecoration: 'line-through' }}>
            {p.value}
          </Box>
        ) : p.added ? (
          <Box key={i} component="ins" sx={{ bgcolor: 'success.main', color: 'success.contrastText', textDecoration: 'none', borderRadius: 0.5, px: 0.25 }}>
            {p.value}
          </Box>
        ) : (
          <span key={i}>{p.value}</span>
        ),
      )}
    </span>
  )
}
