/** Main application layout — navigation sidebar + content area. */

import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/governance', label: 'Governance' },
  { to: '/intelligence', label: 'Intelligence' },
  { to: '/jarvis', label: 'Jarvis · Vibe' },
]

const DISCORD_INVITE = 'https://discord.gg/ZtYmsQRcR'

export default function MainLayout() {
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside
        style={{
          width: 240,
          background: 'var(--color-neutral-900)',
          color: '#fff',
          padding: '1.5rem 1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '2rem',
        }}
      >
        <div>
          <p
            style={{
              fontSize: '0.75rem',
              color: '#9ca3af',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            KCN Ecosystem
          </p>
          <h1 style={{ fontSize: '1.125rem', fontWeight: 700, marginTop: '0.25rem' }}>
            Intelligence Hub
          </h1>
          <p style={{ fontSize: '0.7rem', color: '#6ee7b7', marginTop: '0.35rem' }}>
            Free public demo
          </p>
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', flex: 1 }}>
          {NAV_LINKS.map(({ to, label }) => {
            const active = location.pathname === to || location.pathname.startsWith(to + '/')
            return (
              <Link
                key={to}
                to={to}
                style={{
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius)',
                  color: active ? '#fff' : '#d1d5db',
                  background: active ? 'var(--color-primary)' : 'transparent',
                  fontWeight: active ? 600 : 400,
                  textDecoration: 'none',
                  transition: 'background 0.15s',
                }}
              >
                {label}
              </Link>
            )
          })}

          <Link
            to="/admin"
            style={{
              padding: '0.5rem 0.75rem',
              borderRadius: 'var(--radius)',
              color: location.pathname === '/admin' ? '#fff' : '#d1d5db',
              background: location.pathname === '/admin' ? 'var(--color-primary)' : 'transparent',
              fontWeight: location.pathname === '/admin' ? 600 : 400,
              textDecoration: 'none',
              marginTop: '0.5rem',
            }}
          >
            Admin {isAuthenticated ? '' : '(login)'}
          </Link>

          <a
            href={DISCORD_INVITE}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: '0.5rem 0.75rem',
              borderRadius: 'var(--radius)',
              color: '#d1d5db',
              textDecoration: 'none',
              marginTop: '0.25rem',
            }}
          >
            Discord
          </a>
        </nav>

        <Link
          to="/"
          style={{
            fontSize: '0.8rem',
            color: '#9ca3af',
            textDecoration: 'none',
          }}
        >
          ← Home
        </Link>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: '2rem' }}>
        <Outlet />
      </main>
    </div>
  )
}
