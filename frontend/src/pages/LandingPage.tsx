/** Public landing page — free demo hero + call-to-action. */

import { Link } from 'react-router-dom'

const DISCORD_INVITE = 'https://discord.gg/ZtYmsQRcR'

export default function LandingPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-neutral-50)' }}>
      {/* Top nav */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 2rem',
          background: '#fff',
          borderBottom: '1px solid var(--color-neutral-200)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span
            style={{
              fontWeight: 700,
              fontSize: '1.125rem',
              color: 'var(--color-primary)',
            }}
          >
            KCN Ecosystem
          </span>
          <span
            style={{
              fontSize: '0.75rem',
              background: 'var(--color-success)',
              color: '#fff',
              padding: '0.15rem 0.5rem',
              borderRadius: '999px',
              fontWeight: 600,
            }}
          >
            Free Demo
          </span>
        </div>
        <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Link to="/dashboard" style={{ fontWeight: 500 }}>
            Try Demo
          </Link>
          <a
            href={DISCORD_INVITE}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontWeight: 500 }}
          >
            Discord
          </a>
          <Link
            to="/login"
            style={{
              background: 'var(--color-primary)',
              color: '#fff',
              padding: '0.4rem 1rem',
              borderRadius: 'var(--radius)',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            Admin Login
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section
        style={{
          maxWidth: 900,
          margin: '0 auto',
          padding: '4rem 1.5rem 3rem',
          textAlign: 'center',
        }}
      >
        <p
          style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--color-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '0.75rem',
          }}
        >
          Human-Governed Intelligence
        </p>
        <h1
          style={{
            fontSize: 'clamp(1.75rem, 5vw, 2.75rem)',
            fontWeight: 800,
            lineHeight: 1.2,
            marginBottom: '1.25rem',
            color: 'var(--color-neutral-900)',
          }}
        >
          KCN Super Cognitive Human Governed Intelligence Ecosystem
        </h1>
        <p
          style={{
            fontSize: '1.125rem',
            color: '#4b5563',
            maxWidth: 640,
            margin: '0 auto 2rem',
            lineHeight: 1.6,
          }}
        >
          A modular platform where AI enhances human capability while humans
          keep authority, accountability, and final decision-making control.
          Built to expand human potential with trust, transparency, and
          governance at the core.
        </p>

        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '1rem',
            justifyContent: 'center',
            marginBottom: '1.5rem',
          }}
        >
          <Link
            to="/dashboard"
            style={{
              background: 'var(--color-primary)',
              color: '#fff',
              padding: '0.75rem 1.75rem',
              borderRadius: 'var(--radius)',
              fontWeight: 700,
              fontSize: '1rem',
              textDecoration: 'none',
              boxShadow: 'var(--shadow)',
            }}
          >
            Explore Free Public Demo
          </Link>
          <a
            href={DISCORD_INVITE}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              background: '#5865F2',
              color: '#fff',
              padding: '0.75rem 1.75rem',
              borderRadius: 'var(--radius)',
              fontWeight: 700,
              fontSize: '1rem',
              textDecoration: 'none',
              boxShadow: 'var(--shadow)',
            }}
          >
            Join Discord Community
          </a>
        </div>

        <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
          Public demo is free for 2 weeks · Admin access is always free
        </p>
      </section>

      {/* Feature cards */}
      <section
        style={{
          maxWidth: 1000,
          margin: '0 auto',
          padding: '0 1.5rem 4rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {[
          {
            title: 'Human Governance',
            desc: 'Rules, oversight, and final authority stay with people.',
          },
          {
            title: 'Intelligence Core',
            desc: 'Research, reasoning, planning, and analysis modules.',
          },
          {
            title: 'Verification & Trust',
            desc: 'Evidence checks, fact-checking, and reliability gates.',
          },
          {
            title: 'Security First',
            desc: 'Identity, auth, encryption, and continuous monitoring.',
          },
        ].map(({ title, desc }) => (
          <div
            key={title}
            style={{
              background: '#fff',
              borderRadius: 'var(--radius)',
              boxShadow: 'var(--shadow)',
              padding: '1.5rem',
              borderTop: '3px solid var(--color-primary)',
            }}
          >
            <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>{title}</h3>
            <p style={{ fontSize: '0.9rem', color: '#4b5563' }}>{desc}</p>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer
        style={{
          textAlign: 'center',
          padding: '2rem',
          borderTop: '1px solid var(--color-neutral-200)',
          color: '#6b7280',
          fontSize: '0.875rem',
        }}
      >
        <p>
          Built by Evan Ketchum · Open source ·{' '}
          <a
            href="https://github.com/Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>{' '}
          ·{' '}
          <a href={DISCORD_INVITE} target="_blank" rel="noopener noreferrer">
            Discord
          </a>
        </p>
      </footer>
    </div>
  )
}
