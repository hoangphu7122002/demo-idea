import LinearProgress from '@mui/material/LinearProgress'
import Box from '@mui/material/Box'
import { useParams } from 'react-router'
import '../features/post/postFonts'
import { MdxContent } from '../features/post/MdxContent'
import { useGetPostQuery } from '../features/post/postApi'
import { LOCAL_POSTS } from '../features/post/posts'
import { NotFoundPage } from './NotFoundPage'

export function PostPage() {
  const { slug = '' } = useParams()
  const { data, isLoading } = useGetPostQuery(slug)
  const local = LOCAL_POSTS[slug]
  if (isLoading) return <LinearProgress aria-label="Loading post" />
  // API first; the bundled fixture is the offline fallback.
  if (!data && !local) return <NotFoundPage />
  const body = data ? <MdxContent source={data.source} /> : local && <local.Content />
  return (
    <Box
      component="article"
      data-testid="post-body"
      sx={{
        maxWidth: 720,
        mx: 'auto',
        fontFamily: '"Crimson Pro", Georgia, serif',
        fontSize: '1.25rem',
        lineHeight: 1.7,
        '& h1, & h2': { fontFamily: 'Inter, system-ui, sans-serif', lineHeight: 1.25, mt: 4, mb: 2 },
        '& pre': { p: 2, borderRadius: 1, overflowX: 'auto', fontSize: '0.9rem', lineHeight: 1.5 },
        '& code': { fontFamily: '"JetBrains Mono", ui-monospace, monospace', fontSize: '0.9em' },
        '& .katex-display': { overflowX: 'auto', overflowY: 'hidden' },
      }}
    >
      {body}
    </Box>
  )
}
