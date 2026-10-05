import LinearProgress from '@mui/material/LinearProgress'
import Box from '@mui/material/Box'
import { useRef, useState } from 'react'
import { useParams } from 'react-router'
import '../features/post/postFonts'
import { MdxContent } from '../features/post/MdxContent'
import { useGetPostQuery } from '../features/post/postApi'
import { suggestEnabled } from '../features/suggest/flag'
import { ModerationPanel } from '../features/moderation/ModerationPanel'
import { SuggestLayer } from '../features/suggest/SuggestLayer'
import { LOCAL_POSTS } from '../features/post/posts'
import { RevisionLayer } from '../features/revision/RevisionLayer'
import { latestSpanRevision } from '../features/revision/revisionMeta'
import { ShowChangesToggle } from '../features/revision/ShowChangesToggle'
import { NotFoundPage } from './NotFoundPage'

export function PostPage() {
  const { slug = '' } = useParams()
  const articleRef = useRef<HTMLElement>(null)
  const { data, isLoading } = useGetPostQuery(slug)
  const [showChanges, setShowChanges] = useState(false)
  const local = LOCAL_POSTS[slug]
  if (isLoading) return <LinearProgress aria-label="Loading post" />
  // API first; the bundled fixture is the offline fallback.
  if (!data && !local) return <NotFoundPage />
  const revision = latestSpanRevision(data?.revisions)
  const body = data ? <MdxContent source={data.source} /> : local && <local.Content />
  const article = (
    <Box
      component="article"
      ref={articleRef}
      data-testid="post-body"
      sx={{
        maxWidth: 720,
        mx: 'auto',
        flex: 1,
        minWidth: 0,
        fontFamily: '"Crimson Pro", Georgia, serif',
        fontSize: '1.25rem',
        lineHeight: 1.7,
        '& h1, & h2': { fontFamily: 'Inter, system-ui, sans-serif', lineHeight: 1.25, mt: 4, mb: 2 },
        '& pre': { p: 2, borderRadius: 1, overflowX: 'auto', fontSize: '0.9rem', lineHeight: 1.5 },
        '& code': { fontFamily: '"JetBrains Mono", ui-monospace, monospace', fontSize: '0.9em' },
        '& .katex-display': { overflowX: 'auto', overflowY: 'hidden' },
      }}
    >
      {revision && <ShowChangesToggle checked={showChanges} onChange={setShowChanges} />}
      {body}
      {revision && data && <RevisionLayer containerRef={articleRef} source={data.source} revision={revision} showChanges={showChanges} />}
      {suggestEnabled() && <SuggestLayer slug={slug} containerRef={articleRef} source={data?.source ?? null} />}
    </Box>
  )
  if (!suggestEnabled()) return article
  return (
    <Box sx={{ display: 'flex', gap: 4, alignItems: 'flex-start' }}>
      {article}
      <ModerationPanel slug={slug} />
    </Box>
  )
}
