import Box from '@mui/material/Box'
import { useParams } from 'react-router'
import '../features/post/postFonts'
import { LOCAL_POSTS } from '../features/post/posts'
import { NotFoundPage } from './NotFoundPage'

export function PostPage() {
  const { slug = '' } = useParams()
  const post = LOCAL_POSTS[slug]
  if (!post) return <NotFoundPage />
  const { Content } = post
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
      <Content />
    </Box>
  )
}
