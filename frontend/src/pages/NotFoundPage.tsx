/** 404 Not Found page. */

import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>404</h2>
      <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
        The page you are looking for does not exist.
      </p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link
          to="/"
          style={{
            background: 'var(--color-primary)',
            color: '#fff',
            padding: '0.5rem 1.25rem',
            borderRadius: 'var(--radius)',
            fontWeight: 600,
            textDecoration: 'none',
          }}
        >
          Home
        </Link>
        <Link
          to="/dashboard"
          style={{
            border: '1px solid var(--color-primary)',
            color: 'var(--color-primary)',
            padding: '0.5rem 1.25rem',
            borderRadius: 'var(--radius)',
            fontWeight: 600,
            textDecoration: 'none',
          }}
        >
          Public Demo
        </Link>
      </div>
    </div>
  )
}
