/** Login page — admin authentication (always free). */

import { FormEvent, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { login } from '../services/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
  github_auth_failed: 'GitHub sign-in failed. Please try again.',
  not_authorized: 'That GitHub account is not authorized for admin access.',
}

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [searchParams] = useSearchParams()
  const oauthError = searchParams.get('error')
  const [error, setError] = useState<string | null>(
    oauthError ? OAUTH_ERROR_MESSAGES[oauthError] ?? 'Sign-in failed.' : null,
  )
  const [loading, setLoading] = useState(false)
  const setTokens = useAuthStore((s) => s.setTokens)
  const navigate = useNavigate()

  function handleGitHubLogin() {
    window.location.href = `${API_BASE_URL}/auth/github/login`
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const tokens = await login(username, password)
      setTokens(tokens.access_token, tokens.refresh_token)
      navigate('/admin')
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data
              ?.detail ?? 'Login failed'
          : 'Login failed. Check credentials and try again.'
      setError(String(message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--color-neutral-50)',
        padding: '1.5rem',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          padding: '2rem',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <p
            style={{
              fontSize: '0.75rem',
              color: '#6b7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            KCN Ecosystem
          </p>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginTop: '0.25rem' }}>
            Admin Login
          </h1>
          <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
            Admin access is always free
          </p>
        </div>

        <button
          type="button"
          onClick={handleGitHubLogin}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            background: '#24292f',
            color: '#fff',
            padding: '0.7rem',
            border: 'none',
            borderRadius: 'var(--radius)',
            fontWeight: 600,
            fontSize: '0.95rem',
            cursor: 'pointer',
            marginBottom: '1.25rem',
          }}
        >
          <svg height="18" viewBox="0 0 16 16" width="18" fill="currentColor" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
              0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
              -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
              .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
              -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0
              1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82
              1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
              0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
          Sign in with GitHub
        </button>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            margin: '0 0 1.25rem',
            color: '#9ca3af',
            fontSize: '0.75rem',
          }}
        >
          <div style={{ flex: 1, height: 1, background: 'var(--color-neutral-200)' }} />
          OR
          <div style={{ flex: 1, height: 1, background: 'var(--color-neutral-200)' }} />
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label
              htmlFor="username"
              style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.35rem' }}
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                border: '1px solid var(--color-neutral-200)',
                borderRadius: 'var(--radius)',
                fontSize: '1rem',
              }}
            />
          </div>
          <div>
            <label
              htmlFor="password"
              style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.35rem' }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem',
                border: '1px solid var(--color-neutral-200)',
                borderRadius: 'var(--radius)',
                fontSize: '1rem',
              }}
            />
          </div>

          {error && (
            <p style={{ color: 'var(--color-danger)', fontSize: '0.875rem' }}>{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              background: 'var(--color-primary)',
              color: '#fff',
              padding: '0.7rem',
              border: 'none',
              borderRadius: 'var(--radius)',
              fontWeight: 600,
              fontSize: '1rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
          <Link to="/">← Back to home</Link>
          {' · '}
          <Link to="/dashboard">Public demo</Link>
        </p>

        <p
          style={{
            marginTop: '1.25rem',
            fontSize: '0.75rem',
            color: '#9ca3af',
            textAlign: 'center',
            lineHeight: 1.4,
          }}
        >
          Demo credentials: <code>admin</code> / <code>changeme</code>
        </p>
      </div>
    </div>
  )
}
