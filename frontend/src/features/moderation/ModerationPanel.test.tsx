import { screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../../api/client'
import { renderApp } from '../../test/render'

const ok = (data: unknown) => ({ data, error: undefined, response: { ok: true, status: 200 } }) as never
const sug = (id: number, status: string, over = {}) => ({
  id, status, original_text: `orig ${id}`, replacement: `fix ${id}`, name: null, reason: null,
  anchor_start: null, anchor_end: null, paragraph_id: null, spam_score: null, created_at: '2026-10-04T00:00:00Z', ...over,
})
const post = { slug: 'x', title: 'T', source: '# Title\n\nHello.\n', revisions: [] }

describe('moderation panel', () => {
  let store: ReturnType<typeof sug>[]
  beforeEach(() => {
    vi.stubEnv('VITE_FEATURE_SUGGEST', 'true')
    store = [sug(1, 'pending', { name: 'Lan' }), sug(2, 'pending'), sug(3, 'filtered')]
    vi.spyOn(api, 'GET').mockImplementation((async (url: string, init: { params?: { query?: { status?: string } } }) => {
      if (url === '/api/posts/{slug}') return ok(post)
      return ok(store.map((s) => ({ ...s })).filter((s) => s.status === init.params?.query?.status))
    }) as never)
  })
  afterEach(() => vi.unstubAllEnvs())

  it('lists pending and filtered separately, and Run filter moves spam', async () => {
    const post_ = vi.spyOn(api, 'POST').mockImplementation((async () => {
      store = store.map((s) => (s.id === 2 ? { ...s, status: 'filtered' } : s)) // RTK freezes served objects
      return ok({ checked: 2, spam: 1, ham: 1, filtered_total: 2 })
    }) as never)
    const { user } = renderApp('/posts/x')
    const pending = await screen.findByTestId('pending-list')
    expect(await within(pending).findByText('fix 1')).toBeTruthy()
    expect(within(pending).getByText('Lan')).toBeTruthy()
    expect(within(pending).getByText('a reader')).toBeTruthy()
    expect((await screen.findByTestId('filtered-count')).textContent).toBe('1')
    expect((within(pending).getByTestId('approve-1') as HTMLButtonElement).disabled).toBe(true)

    await user.click(screen.getByTestId('run-filter'))
    await waitFor(() => expect(post_).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByTestId('filtered-count').textContent).toBe('2'))
    expect(screen.getByTestId('pending-count').textContent).toBe('1')
    expect(within(screen.getByTestId('filtered-list')).getByText('fix 2')).toBeTruthy()
  })

  it('shows no panel when the flag is off', async () => {
    vi.stubEnv('VITE_FEATURE_SUGGEST', 'false')
    renderApp('/posts/x')
    await screen.findByRole('heading', { name: 'Title' })
    expect(screen.queryByTestId('moderation-panel')).toBeNull()
  })
})
