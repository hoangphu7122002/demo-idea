import { mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { test } from '@playwright/test'

// Env: SHOT_ROUTES (comma-separated, default "/"), SHOT_BASE_URL, SHOT_OUT_DIR
const routes = (process.env.SHOT_ROUTES ?? '/')
  .split(',')
  .map((r) => r.trim())
  .filter(Boolean)
const baseURL = process.env.SHOT_BASE_URL ?? 'http://127.0.0.1:4173'
const outDir = process.env.SHOT_OUT_DIR ?? '../.test-report/shots/head'

test.use({ viewport: { width: 1280, height: 800 }, baseURL })

const slug = (r: string) => (r === '/' ? 'index' : r.replace(/^\/+/, '').replace(/[^a-zA-Z0-9]+/g, '_'))

for (const route of routes) {
  test(`shot ${route}`, async ({ page }) => {
    mkdirSync(outDir, { recursive: true })
    await page.goto(route, { waitUntil: 'networkidle' })
    await page.screenshot({ path: join(outDir, `${slug(route)}.png`), fullPage: false })
  })
}
