/** Governance page — list policies and submit approval requests. */

import { useEffect, useState } from 'react'
import type { Policy } from '../types/api'
import { listPolicies, submitApproval } from '../services/governance'

export default function GovernancePage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [approvalDescription, setApprovalDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState<string | null>(null)

  useEffect(() => {
    listPolicies()
      .then((data) => setPolicies(data.policies))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleApprovalSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!approvalDescription.trim()) return
    setSubmitting(true)
    try {
      const result = await submitApproval({
        action_type: 'user_request',
        description: approvalDescription,
      })
      setSubmitted(result.id)
      setApprovalDescription('')
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
        Governance
      </h2>

      {/* Policies */}
      <section style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Active Policies</h3>
        {loading && <p style={{ color: '#6b7280' }}>Loading policies…</p>}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {policies.map((policy) => (
            <div
              key={policy.id}
              style={{
                background: '#fff',
                borderRadius: 'var(--radius)',
                boxShadow: 'var(--shadow-sm)',
                padding: '1rem 1.25rem',
                borderLeft: `4px solid ${policy.enabled ? 'var(--color-success)' : '#9ca3af'}`,
              }}
            >
              <p style={{ fontWeight: 600 }}>{policy.name}</p>
              <p style={{ fontSize: '0.875rem', color: '#4b5563', marginTop: '0.25rem' }}>
                {policy.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Approval Request Form */}
      <section>
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Submit Approval Request</h3>
        <form
          onSubmit={handleApprovalSubmit}
          style={{
            background: '#fff',
            borderRadius: 'var(--radius)',
            boxShadow: 'var(--shadow-sm)',
            padding: '1.5rem',
            maxWidth: 480,
          }}
        >
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Description
          </label>
          <textarea
            value={approvalDescription}
            onChange={(e) => setApprovalDescription(e.target.value)}
            rows={4}
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--color-neutral-200)',
              fontFamily: 'inherit',
              fontSize: '0.875rem',
              marginBottom: '1rem',
            }}
            placeholder="Describe the action requiring human approval…"
          />
          <button
            type="submit"
            disabled={submitting}
            style={{
              background: 'var(--color-primary)',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius)',
              padding: '0.5rem 1.25rem',
              cursor: submitting ? 'not-allowed' : 'pointer',
              fontWeight: 600,
            }}
          >
            {submitting ? 'Submitting…' : 'Submit for Approval'}
          </button>
          {submitted && (
            <p style={{ marginTop: '0.75rem', color: 'var(--color-success)', fontSize: '0.875rem' }}>
              Approval request submitted: {submitted}
            </p>
          )}
        </form>
      </section>
    </div>
  )
}
