import { cleanup, configure } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
  localStorage.clear()
})

// jsdom lacks matchMedia, which MUI's colour-scheme manager needs.
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList
}

// Lazy route chunks (MDX + Shiki + KaTeX) can take >1s to transform on a cold cache.
configure({ asyncUtilTimeout: 10_000 })
