import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../../api/client'
import { renderApp } from '../../test/render'
import { creditLabel, unescapeMdx } from './revisionMeta'

const source = 'Intro line about quorum.\n\nA majority is more than half. Quorum is half.\n\n```js\nconst quorum = 1\n```\n'
const newText = 'more than half'
const start = source.indexOf(newText)

function mockPost(credit: string | null) {
  vi.spyOn(api, 'GET').mockResolvedValue({
    data: {
      slug: 'x',
      title: 'T',
      source,
      revisions: [{ number: 2, created_at: '2026-10-05T00:00:00Z', credit_name: credit, previous_text: 'at least half', change_start: start, change_end: start + newText.length }],
    },
    error: undefined,
    response: { ok: true, status: 200 },
  } as never)
}

describe('revision layer', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('shows credit with toggle off, diff with toggle on', async () => {
    mockPost('Ada')
    renderApp('/posts/x')
    expect(await screen.findByTestId('credit-badge')).toHaveProperty('textContent', 'fixed by Ada')
    const body = screen.getByTestId('post-body')
    expect(body.querySelector('del')).toBeNull()
    expect(body.textContent).toContain('A majority is more than half')
    await userEvent.click(screen.getByRole('switch', { name: /show changes/i }))
    expect(body.querySelector('del')?.textContent).toContain('at least')
    expect(body.querySelector('ins')?.textContent).toContain('more than')
    await userEvent.click(screen.getByRole('switch', { name: /show changes/i }))
    expect(screen.getByTestId('credit-badge')).toBeTruthy()
  })

  it('falls back to "a reader" for anonymous credit', async () => {
    mockPost(null)
    renderApp('/posts/x')
    expect((await screen.findByTestId('credit-badge')).textContent).toBe('fixed by a reader')
  })

  it('meta helpers', () => {
    expect(creditLabel('  ')).toBe('fixed by a reader')
    expect(unescapeMdx('a \\{b\\} \\<c\\>')).toBe('a {b} <c>')
  })
})
