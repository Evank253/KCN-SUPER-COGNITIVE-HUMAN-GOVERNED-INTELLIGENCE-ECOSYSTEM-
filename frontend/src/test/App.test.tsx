/** Tests for App routing. */

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from '../App'

// Mock useHealth to avoid fetch calls in tests
import { vi } from 'vitest'
vi.mock('../hooks/useHealth', () => ({
  useHealth: () => ({
    health: { status: 'healthy', version: '0.1.0', timestamp: '2026-08-01T00:00:00Z' },
    loading: false,
    error: null,
  }),
}))

describe('App', () => {
  it('renders the dashboard on the root path', () => {
    render(<App />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders the navigation sidebar', () => {
    render(<App />)
    expect(screen.getByText('Governance')).toBeInTheDocument()
    expect(screen.getByText('Intelligence')).toBeInTheDocument()
  })
})
