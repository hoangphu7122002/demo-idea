import { screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { renderApp } from '../test/render'

const fail = () => ({ data: undefined, error: {}, response: { ok: false, status: 503 } }) as never

describe('PostPage', () => {
  beforeEach(() => {
    vi.spyOn(api, 'GET').mockResolvedValue(fail())
  })

  it('renders API source via runtime MDX', async () => {
    vi.spyOn(api, 'GET').mockResolvedValue({
      data: { slug: 'x', title: 'T', source: '# From API\n\nHello $a^2$ world.\n', revisions: [] },
      error: undefined,
      response: { ok: true, status: 200 },
    } as never)
    renderApp('/posts/x')
    expect(await screen.findByRole('heading', { name: 'From API' })).toBeTruthy()
    const body = screen.getByTestId('post-body')
    expect(body.querySelector('.katex')).not.toBeNull()
    expect(body.querySelector('p')?.hasAttribute('data-src-start')).toBe(true)
  })

  it('falls back to the local fixture when the API is down', async () => {
    renderApp('/posts/raft-consensus-in-practice')
    expect(await screen.findByRole('heading', { name: /why raft needs a majority/i })).toBeTruthy()
  })

  it('renders MDX with highlighted code, KaTeX and source anchors', async () => {
    renderApp('/posts/raft-quorum')
    expect(await screen.findByRole('heading', { name: /why raft needs a majority/i })).toBeTruthy()
    const body = screen.getByTestId('post-body')
    expect(body.querySelector('.katex')).not.toBeNull()
    expect(body.textContent).not.toMatch(/\$\$|\$\\lfloor/)
    expect(body.querySelector('pre.shiki')).not.toBeNull()
    const anchored = body.querySelectorAll('[data-src-start]')
    expect(anchored.length).toBeGreaterThan(4)
    expect(body.querySelector('p')?.getAttribute('data-src-end')).toBeTruthy()
    expect(body.querySelector('pre')?.hasAttribute('data-src-start')).toBe(true)
  })

  it('shows not found for unknown slug', async () => {
    renderApp('/posts/nope')
    expect(await screen.findByText(/not found/i)).toBeTruthy()
  })
})
