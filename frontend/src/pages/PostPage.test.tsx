import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderApp } from '../test/render'

describe('PostPage', () => {
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
