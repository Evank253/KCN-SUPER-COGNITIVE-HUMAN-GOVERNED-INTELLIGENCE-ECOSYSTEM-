/** Dashboard page — ecosystem overview and health status. */

import { useHealth } from '../hooks/useHealth'

export default function DashboardPage() {
  const { health, loading, error } = useHealth()

  return (
    <div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
        Dashboard
      </h2>

      {/* System Status Card */}
      <section
        style={{
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          maxWidth: 480,
        }}
      >
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>System Status</h3>
        {loading && <p style={{ color: '#6b7280' }}>Checking backend status…</p>}
        {error && <p style={{ color: 'var(--color-danger)' }}>Backend unavailable: {error}</p>}
        {health && (
          <dl style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '0.5rem' }}>
            <dt style={{ fontWeight: 500 }}>Status</dt>
            <dd style={{ color: 'var(--color-success)', fontWeight: 600 }}>{health.status}</dd>
            <dt style={{ fontWeight: 500 }}>Version</dt>
            <dd>{health.version}</dd>
            <dt style={{ fontWeight: 500 }}>Timestamp</dt>
            <dd style={{ fontSize: '0.875rem', color: '#6b7280' }}>{health.timestamp}</dd>
          </dl>
        )}
      </section>

      {/* Ecosystem Summary */}
      <section>
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Ecosystem Modules</h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
            gap: '1rem',
          }}
        >
          {[
            { name: 'Governance', status: 'Active' },
            { name: 'Intelligence Core', status: 'Phase 2' },
            { name: 'Verification Core', status: 'Phase 3' },
            { name: 'Security Core', status: 'Phase 2' },
            { name: 'Knowledge Core', status: 'Phase 3' },
            { name: 'Education System', status: 'Phase 4' },
            { name: 'Innovation System', status: 'Phase 5' },
            { name: 'Analytics', status: 'Phase 6' },
          ].map(({ name, status }) => (
            <div
              key={name}
              style={{
                background: '#fff',
                borderRadius: 'var(--radius)',
                boxShadow: 'var(--shadow-sm)',
                padding: '1rem',
                borderLeft: '4px solid var(--color-primary)',
              }}
            >
              <p style={{ fontWeight: 600, fontSize: '0.875rem' }}>{name}</p>
              <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                {status}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
