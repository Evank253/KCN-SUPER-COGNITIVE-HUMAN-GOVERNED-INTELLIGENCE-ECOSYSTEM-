/** Admin dashboard — protected, always free. */

import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function AdminPage() {
  const clearTokens = useAuthStore((s) => s.clearTokens)
  const navigate = useNavigate()

  function handleLogout() {
    clearTokens()
    navigate('/login')
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
        }}
      >
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Admin</h2>
        <button
          type="button"
          onClick={handleLogout}
          style={{
            background: 'transparent',
            border: '1px solid var(--color-neutral-200)',
            borderRadius: 'var(--radius)',
            padding: '0.4rem 0.9rem',
            cursor: 'pointer',
            fontWeight: 500,
          }}
        >
          Log out
        </button>
      </div>

      <section
        style={{
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          padding: '1.5rem',
          marginBottom: '1.5rem',
        }}
      >
        <h3 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>Welcome, Admin</h3>
        <p style={{ color: '#4b5563', marginBottom: '1rem' }}>
          You are signed in to the admin area. Admin access is always free.
        </p>
        <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          This area is reserved for operators and maintainers. Public visitors
          use the free demo pages without an account.
        </p>
      </section>

      <section
        style={{
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          padding: '1.5rem',
        }}
      >
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Quick links</h3>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <li>
            <Link to="/dashboard">Public Dashboard</Link>
          </li>
          <li>
            <Link to="/governance">Governance</Link>
          </li>
          <li>
            <Link to="/intelligence">Intelligence</Link>
          </li>
          <li>
            <a
              href="https://discord.gg/ZtYmsQRcR"
              target="_blank"
              rel="noopener noreferrer"
            >
              Discord Community
            </a>
          </li>
        </ul>
      </section>
    </div>
  )
}
