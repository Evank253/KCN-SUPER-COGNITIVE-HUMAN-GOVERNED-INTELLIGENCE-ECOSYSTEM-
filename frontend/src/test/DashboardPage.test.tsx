/** Tests for DashboardPage component. */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import DashboardPage from '../pages/DashboardPage'

// Mock the useHealth hook
vi.mock('../hooks/useHealth', () => ({
  useHealth: () => ({
    health: { status: 'healthy', version: '0.1.0', timestamp: '2026-08-01T00:00:00Z' },
    loading: false,
    error: null,
  }),
}))

describe('DashboardPage', () => {
  it('renders the Dashboard heading', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders health status when available', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    expect(screen.getByText('healthy')).toBeInTheDocument()
    expect(screen.getByText('0.1.0')).toBeInTheDocument()
  })

  it('renders ecosystem module cards', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    expect(screen.getByText('Governance')).toBeInTheDocument()
    expect(screen.getByText('Intelligence Core')).toBeInTheDocument()
    expect(screen.getByText('Verification Core')).toBeInTheDocument()
  })
})
