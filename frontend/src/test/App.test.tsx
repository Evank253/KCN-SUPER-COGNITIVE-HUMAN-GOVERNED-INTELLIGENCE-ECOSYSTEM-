/** Tests for App routing. */

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from '../App'

// Mock useHealth to avoid fetch calls in tests
vi.mock('../hooks/useHealth', () => ({
  useHealth: () => ({
    health: { status: 'healthy', version: '0.1.0', timestamp: '2026-08-01T00:00:00Z' },
    loading: false,
    error: null,
  }),
}))

describe('App', () => {
  it('renders the public landing page on the root path', () => {
    render(<App />)
    expect(
      screen.getByRole('heading', {
        name: /KCN Super Cognitive Human Governed Intelligence Ecosystem/i,
      }),
    ).toBeInTheDocument()
  })

  it('shows Discord community link on the landing page', () => {
    render(<App />)
    const links = screen.getAllByRole('link', { name: /Discord/i })
    expect(links.length).toBeGreaterThan(0)
  })
})
