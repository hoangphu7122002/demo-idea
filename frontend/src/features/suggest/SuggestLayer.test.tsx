import { act, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../../api/client'
import { renderApp } from '../../test/render'

const SOURCE = '# Title\n\nA cluster needs exactly 3 nodes to survive one failure.\n\n```ts\nconst quorum = 2\n```\n'
const post = { slug: 'x', title: 'T', source: SOURCE, revisions: [] }
const ok = (data: unknown) => ({ data, error: undefined, response: { ok: true, status: 200 } }) as never

function select(node: Node, from: number, to: number) {
  const range = document.createRange()
  range.setStart(node, from)
  range.setEnd(node, to)
  range.getBoundingClientRect = () => new DOMRect(10, 10, 100, 20)
  const sel = window.getSelection()!
  sel.removeAllRanges()
  sel.addRange(range)
  return range
}

async function openPost() {
  const utils = renderApp('/posts/x')
  await screen.findByRole('heading', { name: 'Title' })
  return utils
}

describe('suggestion popup', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_FEATURE_SUGGEST', 'true')
    vi.spyOn(api, 'GET').mockResolvedValue(ok(post))
  })
  afterEach(() => vi.unstubAllEnvs())

  it('maps a prose selection to a span anchor and submits anonymously', async () => {
    const posted = vi.spyOn(api, 'POST').mockResolvedValue(ok({ id: 1 }))
    const { user } = await openPost()
    const body = screen.getByTestId('post-body')
    const text = body.querySelector('p')!.firstChild!
    const at = text.textContent!.indexOf('exactly 3 nodes')
    select(text, at, at + 'exactly 3 nodes'.length)
    act(() => {
      body.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    })
    expect(await screen.findByTestId('suggest-popup')).toBeTruthy()
    await user.type(screen.getByTestId('suggest-replacement'), 'at least 2f+1 nodes')
    await user.type(screen.getByTestId('suggest-name'), 'Lan')
    await user.click(screen.getByTestId('suggest-submit'))
    await waitFor(() => expect(posted).toHaveBeenCalled())
    const args = posted.mock.calls[0][1] as { body: Record<string, unknown> }
    const start = SOURCE.indexOf('exactly 3 nodes')
    expect(args.body).toMatchObject({
      original_text: 'exactly 3 nodes',
      replacement: 'at least 2f+1 nodes',
      name: 'Lan',
      anchor_start: start,
      anchor_end: start + 'exactly 3 nodes'.length,
    })
    expect(await screen.findByText(/suggestion sent/i)).toBeTruthy()
    await waitFor(() => expect(screen.queryByTestId('suggest-popup')).toBeNull())
  })

  it('blocks an empty replacement with an inline message', async () => {
    const posted = vi.spyOn(api, 'POST')
    const { user } = await openPost()
    const body = screen.getByTestId('post-body')
    const text = body.querySelector('p')!.firstChild!
    select(text, 2, 9)
    act(() => {
      body.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    })
    await user.click(await screen.findByTestId('suggest-submit'))
    expect(await screen.findByText(/replacement text is required/i)).toBeTruthy()
    expect(posted).not.toHaveBeenCalled()
  })

  it('uses paragraph-level anchors inside code blocks', async () => {
    await openPost()
    const body = screen.getByTestId('post-body')
    const pre = body.querySelector('pre')!
    const walker = document.createTreeWalker(pre, NodeFilter.SHOW_TEXT)
    const node = walker.nextNode()!
    select(node, 0, 5)
    act(() => {
      body.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    })
    expect((await screen.findByTestId('suggest-level')).textContent).toMatch(/in this paragraph/i)
  })
})

describe('feature flag', () => {
  it('shows no popup when VITE_FEATURE_SUGGEST is off', async () => {
    vi.stubEnv('VITE_FEATURE_SUGGEST', 'false')
    vi.spyOn(api, 'GET').mockResolvedValue(ok(post))
    await openPost()
    const body = screen.getByTestId('post-body')
    select(body.querySelector('p')!.firstChild!, 2, 9)
    act(() => {
      body.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    })
    expect(screen.queryByTestId('suggest-popup')).toBeNull()
    vi.unstubAllEnvs()
  })
})
