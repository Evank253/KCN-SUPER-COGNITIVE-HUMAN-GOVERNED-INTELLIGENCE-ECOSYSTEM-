/** Receives the backend's redirect after GitHub OAuth completes, stores tokens, and forwards to /admin. */

import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function AuthCallbackPage() {
  const [searchParams] = useSearchParams()
  const setTokens = useAuthStore((s) => s.setTokens)
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')

    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken)
      navigate('/admin', { replace: true })
      return
    }

    setError('GitHub sign-in did not complete. Please try again.')
  }, [searchParams, setTokens, navigate])

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
      <div style={{ textAlign: 'center' }}>
        {error ? (
          <>
            <p style={{ color: 'var(--color-danger)', marginBottom: '1rem' }}>{error}</p>
            <a href="/login" style={{ color: 'var(--color-primary)' }}>
              Back to login
            </a>
          </>
        ) : (
          <p style={{ color: '#6b7280' }}>Signing you in…</p>
        )}
      </div>
    </div>
  )
}
