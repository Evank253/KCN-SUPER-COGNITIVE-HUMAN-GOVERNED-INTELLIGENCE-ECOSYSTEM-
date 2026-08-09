/** Tests for DashboardPage component. */

import { fireEvent, render, screen } from '@testing-library/react'
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

// Mock the useReadiness hook with a real-shaped component list
vi.mock('../hooks/useReadiness', () => ({
  useReadiness: () => ({
    readiness: {
      status: 'ready',
      version: '0.1.0',
      timestamp: '2026-08-01T00:00:00Z',
      components: [
        { name: 'config', status: 'up', detail: 'settings loaded' },
        { name: 'security', status: 'up', detail: null },
        { name: 'llm_upstream', status: 'degraded', detail: 'no upstream configured' },
      ],
    },
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

  it('renders the KCN Core graph nodes', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    expect(screen.getByText('HUMAN GOVERNANCE')).toBeInTheDocument()
    expect(screen.getByText('SECURITY')).toBeInTheDocument()
    expect(screen.getByText('INTELLIGENCE')).toBeInTheDocument()
    expect(screen.getByText('ASSURANCE')).toBeInTheDocument()
    expect(screen.getByText('KCN CORE')).toBeInTheDocument()
    expect(screen.getByText('EVIDENCE')).toBeInTheDocument()
  })

  it('shows a detail panel with real status when a live-wired node is clicked', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    fireEvent.click(screen.getByRole('button', { name: 'Inspect SECURITY' }))
    expect(screen.getByRole('dialog', { name: 'SECURITY detail panel' })).toBeInTheDocument()
    expect(screen.getByText('UP')).toBeInTheDocument()
  })

  it('honestly labels demo nodes that have no live telemetry yet', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    fireEvent.click(screen.getByRole('button', { name: 'Inspect HUMAN GOVERNANCE' }))
    expect(screen.getByText(/isn't wired to live telemetry yet/i)).toBeInTheDocument()
  })
})
