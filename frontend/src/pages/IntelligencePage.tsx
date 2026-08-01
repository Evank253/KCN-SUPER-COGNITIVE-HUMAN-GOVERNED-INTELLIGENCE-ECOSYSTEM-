/** Intelligence page — submit analysis requests. */

import { useState } from 'react'
import type { AnalysisResponse, IntelligenceModule } from '../types/api'
import { submitAnalysis } from '../services/intelligence'

const MODULES: IntelligenceModule[] = [
  'analysis',
  'research',
  'reasoning',
  'planning',
  'creative',
  'engineering',
  'learning',
]

export default function IntelligencePage() {
  const [query, setQuery] = useState('')
  const [module, setModule] = useState<IntelligenceModule>('analysis')
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await submitAnalysis({ query, module })
      setResult(data)
    } catch (err) {
      setError('Failed to submit analysis request. Is the backend running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        Intelligence Core
      </h2>
      <p style={{ color: '#6b7280', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        Submit queries to the Intelligence Core. All outputs are routed through the Verification Core before results are stored.
      </p>

      <form
        onSubmit={handleSubmit}
        style={{
          background: '#fff',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          padding: '1.5rem',
          maxWidth: 640,
          marginBottom: '1.5rem',
        }}
      >
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem' }}>
            Module
          </label>
          <select
            value={module}
            onChange={(e) => setModule(e.target.value as IntelligenceModule)}
            style={{
              padding: '0.5rem',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--color-neutral-200)',
              fontFamily: 'inherit',
            }}
          >
            {MODULES.map((m) => (
              <option key={m} value={m}>
                {m.charAt(0).toUpperCase() + m.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontWeight: 500, marginBottom: '0.5rem' }}>
            Query
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={5}
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--color-neutral-200)',
              fontFamily: 'inherit',
              fontSize: '0.875rem',
            }}
            placeholder="Enter your analysis query…"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            background: 'var(--color-primary)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius)',
            padding: '0.5rem 1.25rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 600,
          }}
        >
          {loading ? 'Submitting…' : 'Submit Analysis'}
        </button>
      </form>

      {error && (
        <p style={{ color: 'var(--color-danger)', marginBottom: '1rem' }}>{error}</p>
      )}

      {result && (
        <div
          style={{
            background: '#fff',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow-sm)',
            padding: '1.5rem',
            maxWidth: 640,
          }}
        >
          <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Result</h3>
          <dl style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '0.5rem', fontSize: '0.875rem' }}>
            <dt style={{ fontWeight: 500 }}>Result ID</dt>
            <dd style={{ fontFamily: 'monospace' }}>{result.id}</dd>
            <dt style={{ fontWeight: 500 }}>Module</dt>
            <dd>{result.module}</dd>
            <dt style={{ fontWeight: 500 }}>Status</dt>
            <dd style={{ color: 'var(--color-warning)', fontWeight: 600 }}>{result.status}</dd>
            <dt style={{ fontWeight: 500 }}>Created</dt>
            <dd style={{ color: '#6b7280' }}>{result.created_at}</dd>
          </dl>
          <p style={{ marginTop: '1rem', fontSize: '0.8125rem', color: '#6b7280' }}>
            This result is queued for Verification Core evaluation. Full processing will be available in Phase 2.
          </p>
        </div>
      )}
    </div>
  )
}
