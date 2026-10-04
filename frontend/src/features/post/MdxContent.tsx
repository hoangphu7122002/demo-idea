import { evaluate } from '@mdx-js/mdx'
import Alert from '@mui/material/Alert'
import type { ComponentType } from 'react'
import { useEffect, useState } from 'react'
import * as runtime from 'react/jsx-runtime'
import { mdxOptions } from './mdxOptions'

/** Compiles MDX source in the browser (same plugins as the build-time fixtures) and renders it. */
export function MdxContent({ source }: { source: string }) {
  const [state, setState] = useState<{ source: string; Content?: ComponentType; failed?: boolean }>({ source })
  useEffect(() => {
    let live = true
    // format 'md': API source is reader-influenced, so no JSX or {expressions} may execute.
    evaluate(source, { ...runtime, ...(mdxOptions as object), format: 'md' } as never)
      .then((m) => live && setState({ source, Content: m.default }))
      .catch(() => live && setState({ source, failed: true }))
    return () => {
      live = false
    }
  }, [source])
  if (state.source !== source || (!state.Content && !state.failed)) return null
  if (state.failed || !state.Content) return <Alert severity="error">This post could not be rendered.</Alert>
  return <state.Content />
}
