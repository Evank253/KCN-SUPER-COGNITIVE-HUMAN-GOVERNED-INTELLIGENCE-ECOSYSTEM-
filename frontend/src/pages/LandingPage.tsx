/** Public landing — hyperspace WebGL + command chat portal jumps. */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import HyperspacePortal from '../components/HyperspacePortal'

const DISCORD_INVITE = 'https://discord.gg/ZtYmsQRcR'

const DESTINATIONS: Record<string, { path?: string; external?: string; label: string }> = {
  dashboard: { path: '/dashboard', label: 'Dashboard' },
  demo: { path: '/dashboard', label: 'Public Demo' },
  governance: { path: '/governance', label: 'Governance' },
  intelligence: { path: '/intelligence', label: 'Intelligence' },
  jarvis: { path: '/jarvis', label: 'Jarvis · Vibe' },
  vibe: { path: '/jarvis', label: 'Jarvis · Vibe' },
  kronos: { path: '/jarvis', label: 'Jarvis · Vibe' },
  admin: { path: '/login', label: 'Admin Login' },
  login: { path: '/login', label: 'Admin Login' },
  discord: { external: DISCORD_INVITE, label: 'Discord' },
  community: { external: DISCORD_INVITE, label: 'Discord' },
  home: { path: '/', label: 'Home' },
}

function resolveDestination(input: string) {
  const q = input.trim().toLowerCase()
  if (!q) return null
  for (const [key, dest] of Object.entries(DESTINATIONS)) {
    if (q === key || q.includes(key)) return dest
  }
  if (/gov|policy|rule/.test(q)) return DESTINATIONS.governance
  if (/intel|ai|reason|research/.test(q)) return DESTINATIONS.intelligence
  if (/jarvis|vibe|kronos|build|coder/.test(q)) return DESTINATIONS.jarvis
  if (/admin|login|operator/.test(q)) return DESTINATIONS.admin
  if (/discord|chat|community/.test(q)) return DESTINATIONS.discord
  if (/demo|try|start|dash/.test(q)) return DESTINATIONS.dashboard
  return DESTINATIONS.dashboard
}

const navBtn: React.CSSProperties = {
  background: 'rgba(15, 23, 42, 0.5)',
  border: '1px solid rgba(120,160,255,0.25)',
  color: '#e2e8f0',
  padding: '0.35rem 0.85rem',
  borderRadius: '8px',
  fontWeight: 600,
  fontSize: '0.85rem',
  cursor: 'pointer',
}

export default function LandingPage() {
  const navigate = useNavigate()
  const [warp, setWarp] = useState(0)
  const [bootDone, setBootDone] = useState(false)
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('Systems initializing…')
  const [intensity, setIntensity] = useState(0.55)

  useEffect(() => {
    const t1 = window.setTimeout(() => setStatus('Neural lattice online'), 900)
    const t2 = window.setTimeout(() => setStatus('Governance layer linked'), 1600)
    const t3 = window.setTimeout(() => {
      setStatus('Ready — type a destination or click below')
      setBootDone(true)
      setIntensity(0.35)
    }, 2500)
    return () => {
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
    }
  }, [])

  const portalTo = useCallback(
    (dest: { path?: string; external?: string; label: string }) => {
      setWarp((w) => w + 1)
      setIntensity(0.95)
      setStatus(`Opening portal → ${dest.label}`)
      window.setTimeout(() => {
        if (dest.external) {
          window.open(dest.external, '_blank', 'noopener,noreferrer')
          setIntensity(0.35)
          setStatus('Portal standby — enter next command')
        } else if (dest.path) {
          navigate(dest.path)
        }
      }, 900)
    },
    [navigate],
  )

  function handleCommand(e: FormEvent) {
    e.preventDefault()
    const dest = resolveDestination(query)
    if (!dest) return
    setQuery('')
    portalTo(dest)
  }

  const glass: React.CSSProperties = {
    background: 'rgba(8, 12, 28, 0.72)',
    backdropFilter: 'blur(14px)',
    WebkitBackdropFilter: 'blur(14px)',
    border: '1px solid rgba(120, 160, 255, 0.22)',
    borderRadius: '12px',
    boxShadow: '0 0 40px rgba(30, 80, 255, 0.15)',
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        background: '#02040c',
        color: '#e8eefc',
        fontFamily: 'var(--font-sans)',
      }}
    >
      <HyperspacePortal intensity={intensity} warpTrigger={warp} />

      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse at center, transparent 0%, rgba(2,4,12,0.55) 70%, rgba(2,4,12,0.85) 100%)',
          pointerEvents: 'none',
          zIndex: 1,
        }}
      />

      <div
        style={{
          position: 'relative',
          zIndex: 2,
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '1rem 1.75rem',
            borderBottom: '1px solid rgba(120,160,255,0.12)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span
              style={{
                fontWeight: 800,
                letterSpacing: '0.04em',
                background: 'linear-gradient(90deg,#7dd3fc,#a78bfa,#60a5fa)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              KCN ECOSYSTEM
            </span>
            <span
              style={{
                fontSize: '0.7rem',
                background: 'rgba(16,185,129,0.25)',
                color: '#6ee7b7',
                border: '1px solid rgba(16,185,129,0.4)',
                padding: '0.15rem 0.55rem',
                borderRadius: '999px',
                fontWeight: 600,
              }}
            >
              FREE DEMO
            </span>
          </div>
          <nav style={{ display: 'flex', gap: '0.85rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button type="button" onClick={() => portalTo(DESTINATIONS.dashboard)} style={navBtn}>
              Demo
            </button>
            <button type="button" onClick={() => portalTo(DESTINATIONS.jarvis)} style={navBtn}>
              Jarvis
            </button>
            <button type="button" onClick={() => portalTo(DESTINATIONS.discord)} style={navBtn}>
              Discord
            </button>
            <button
              type="button"
              onClick={() => portalTo(DESTINATIONS.admin)}
              style={{
                ...navBtn,
                background: 'rgba(59,130,246,0.35)',
                borderColor: 'rgba(96,165,250,0.5)',
              }}
            >
              Admin
            </button>
          </nav>
        </header>

        <section
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2.5rem 1.25rem 2rem',
            textAlign: 'center',
          }}
        >
          <p
            style={{
              fontSize: '0.8rem',
              fontWeight: 600,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: '#7dd3fc',
              marginBottom: '0.85rem',
              opacity: bootDone ? 1 : 0.6,
              transition: 'opacity 0.6s',
            }}
          >
            Human-Governed Intelligence · Live Systems
          </p>

          <h1
            style={{
              fontSize: 'clamp(1.6rem, 4.5vw, 2.85rem)',
              fontWeight: 800,
              lineHeight: 1.15,
              maxWidth: 820,
              marginBottom: '1rem',
              textShadow: '0 0 40px rgba(80,120,255,0.45)',
            }}
          >
            KCN Super Cognitive Human Governed Intelligence Ecosystem
          </h1>

          <p
            style={{
              fontSize: '1.05rem',
              color: 'rgba(200,210,240,0.82)',
              maxWidth: 580,
              margin: '0 auto 1.75rem',
              lineHeight: 1.55,
            }}
          >
            AI amplifies human capability. Humans keep authority. Type a command or hit a
            node — the portal opens.
          </p>

          <form
            onSubmit={handleCommand}
            style={{
              ...glass,
              width: '100%',
              maxWidth: 520,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.55rem 0.65rem 0.55rem 1rem',
              marginBottom: '0.85rem',
            }}
          {>span<}<
            {<span>}"style"{{ color: '#60a5fa', fontWeight: 700, fontSize: '0.85rem' }{<span>}
             <input
              ,"type="text")
              value={query"
              onChange={(e)=> setQuery(e.target.value)}
              placeholder"portal to jarvis · dashboard · governance · intelligence · admin · discord"
              aria-label="Portal command"
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#e8eefc',
                fontSize: '0.95rem',
                fontFamily: 'inherit',
              }}
           
           <button type>="submit"
              style={{
                background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.5rem 1rem',
                fontWeight: 700,
                cursor: 'pointer',
                fontSize: '0.85rem',
              }}
            >
              Engage
            </button>
          </form>

          <p
            style={{
              fontSize: '0.8rem',
              color: '#93c5fd',
              marginBottom: '1.75rem',
              minHeight: '1.2em',
              letterSpacing: '0.02em',
            }}
          >
            {status}
          </p>

          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.75rem',
              justifyContent: 'center',
              marginBottom: '1.25rem',
            }}
            {(
              [
                ['jarvis', 'Jarvis · Vibe'],
                ['dashboard', 'Public Demo'],
                ['governance', 'Governance'],
                ['intelligence', 'Intelligence'],
                ['admin', 'Admin'],
                ['discord', 'Discord'],
              ] as const
            ).map(([key, label]) => (
              <button type>
                key={key}
                type="button"
                onClick={() => portalTo(DESTINATIONS[key])}
                style={{
                  ...glass,
                  padding: '0.65rem 1.2rem',
                  color: '#e0e7ff',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                }}
              >
                {label}
              </button>
            ))}
          </div>

          <p style={{ fontSize: '0.8rem', color: 'rgba(148,163,184,0.9)' }}>
            Public demo free 2 weeks · Admin always free
          </p>
        </section>

        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '0.85rem',
            padding: '0 1.25rem 2.5rem',
            maxWidth: 1000,
            margin: '0 auto',
            width: '100%',
          }}
        >
          {[
            { t: 'Governance', d: 'Human authority & policy control' },
            { t: 'Intelligence', d: 'Research · reason · plan · create' },
            { t: 'Verification', d: 'Evidence · truth · reliability' },
            { t: 'Jarvis · Vibe', d: 'Speak · build · Kronos hardens' },
          ].map(({ t, d }) => (
            <div key={t} style={{ ...glass, padding: '1.1rem 1.2rem' }}>
              <h3
                style={{
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  marginBottom: '0.35rem',
                  color: '#bfdbfe',
                }}
              >
                {t}
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'rgba(180,190,220,0.75)' }}>{d}</p>
            </div>
          ))}
        </section>

        <footer
          style={{
            textAlign: 'center',
            padding: '1.25rem',
            borderTop: '1px solid rgba(120,160,255,0.1)',
            fontSize: '0.8rem',
            color: 'rgba(148,163,184,0.85)',
          }}
        >
          Built by Evan Ketchum ·{' '}
          <a
            href="https://github.com/Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#93c5fd' }}
          >
            GitHub
          </a>{' '}
          ·{' '}
          <Link to="/jarvis" style={{ color: '#93c5fd' }}>
            Jarvis
          </Link>{' '}
          ·{' '}
          <Link to="/dashboard" style={{ color: '#93c5fd' }}>
            Demo
          </Link>{' '}
          ·{' '}
          <a href={DISCORD_INVITE} target="_blank" rel="noopener noreferrer" style={{ color: '#93c5fd' }}>
            Discord
          </a>
        </footer>
      </div>
    </div>
  )
}
