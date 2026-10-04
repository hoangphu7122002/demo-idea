import { evaluate } from '@mdx-js/mdx'
import type { ComponentType } from 'react'
import { useEffect, useState } from 'react'
import * as runtime from 'react/jsx-runtime'
import { mdxOptions } from './mdxOptions'

/** Compiles MDX source in the browser (same plugins as the build-time fixtures) and renders it. */
export function MdxContent({ source }: { source: string }) {
  const [state, setState] = useState<{ source: string; Content?: ComponentType; failed?: boolean }>({ source })
  useEffect(() => {
    let live = true
    evaluate(source, { ...runtime, ...(mdxOptions as object) } as never)
      .then((m) => live && setState({ source, Content: m.default }))
      .catch(() => live && setState({ source, failed: true }))
    return () => {
      live = false
    }
  }, [source])
  if (state.source !== source || (!state.Content && !state.failed)) return null
  if (state.failed || !state.Content) throw new Error('Could not render post')
  return <state.Content />
}
