import type { ComponentType } from 'react'
import SeedPost from './fixtures/seed-post.mdx'

export type LocalPost = { slug: string; title: string; Content: ComponentType }

/** Local fixtures until the backend posts API lands. */
export const LOCAL_POSTS: Record<string, LocalPost> = {
  'raft-quorum': { slug: 'raft-quorum', title: 'Why Raft needs a majority', Content: SeedPost },
}
