import { defineConfig } from '@playwright/test'

// Only used by scripts/ui-shots.sh (screenshots), not part of `npm test` (vitest).
export default defineConfig({
  testDir: './e2e',
  reporter: 'line',
  workers: 1,
  use: { browserName: 'chromium' },
})
