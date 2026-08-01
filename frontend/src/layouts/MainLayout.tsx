/** Main application layout — navigation sidebar + content area. */

import { Link, Outlet, useLocation } from 'react-router-dom'

const NAV_LINKS = [
  { to: '/', label: 'Dashboard' },
  { to: '/governance', label: 'Governance' },
  { to: '/intelligence', label: 'Intelligence' },
]

export default function MainLayout() {
  const location = useLocation()

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
          <p style={{ fontSize: '0.75rem', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            KCN Ecosystem
          </p>
          <h1 style={{ fontSize: '1.125rem', fontWeight: 700, marginTop: '0.25rem' }}>
            Intelligence Hub
          </h1>
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {NAV_LINKS.map(({ to, label }) => {
            const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
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
        </nav>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: '2rem' }}>
        <Outlet />
      </main>
    </div>
  )
}
