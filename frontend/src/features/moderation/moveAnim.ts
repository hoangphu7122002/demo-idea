import { keyframes } from '@mui/material/styles'

/** Each item's move lasts at least 300 ms (spec F3); items start STAGGER_MS apart. */
export const MOVE_MS = 400
export const STAGGER_MS = 150

export const slideOut = keyframes`
  from { opacity: 1; transform: translateX(0); max-height: 200px; }
  to { opacity: 0; transform: translateX(48px); max-height: 0; }
`
export const slideIn = keyframes`
  from { opacity: 0; transform: translateX(-48px); }
  to { opacity: 1; transform: translateX(0); }
`

/** Time after which every item of an n-item move has landed. */
export const moveTotalMs = (n: number) => MOVE_MS + Math.max(0, n - 1) * STAGGER_MS
