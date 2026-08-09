/**
 * KcnCoreGraph — the layered "living ecosystem" diagram:
 *
 *                HUMAN GOVERNANCE
 *                       |
 *        SECURITY   INTELLIGENCE   ASSURANCE
 *                       |
 *                   KCN CORE
 *                       |
 *                   EVIDENCE
 *
 * Nodes that map to a real backend readiness component (security,
 * intelligence -> llm_upstream) show real live status. Nodes with no
 * backend counterpart yet (governance, assurance, evidence) are clearly
 * labeled as a preview rather than faking a "live" status — see
 * DEMO_NODE_IDS below.
 */

import { useState } from 'react'
import type { ComponentStatus } from '../types/api'

export interface KcnNode {
  id: string
  label: string
  sublabel: string
  x: number
  y: number
  radius: number
  /** Name of the matching /ready component, if one exists. */
  componentName?: string
}

const NODES: KcnNode[] = [
  { id: 'governance', label: 'HUMAN GOVERNANCE', sublabel: 'Highest authority', x: 400, y: 55, radius: 26 },
  { id: 'security', label: 'SECURITY', sublabel: 'Guardian systems', x: 170, y: 225, radius: 24, componentName: 'security' },
  {
    id: 'intelligence',
    label: 'INTELLIGENCE',
    sublabel: 'Reasoning · research',
    x: 400,
    y: 225,
    radius: 24,
    componentName: 'llm_upstream',
  },
  { id: 'assurance', label: 'ASSURANCE', sublabel: 'Trust · verification', x: 630, y: 225, radius: 24 },
  { id: 'core', label: 'KCN CORE', sublabel: 'Cognitive core', x: 400, y: 380, radius: 40, componentName: 'config' },
  { id: 'evidence', label: 'EVIDENCE', sublabel: 'Artifacts · proofs', x: 400, y: 520, radius: 24 },
]

const EDGES: [string, string][] = [
  ['governance', 'security'],
  ['governance', 'intelligence'],
  ['governance', 'assurance'],
  ['security', 'core'],
  ['intelligence', 'core'],
  ['assurance', 'core'],
  ['core', 'evidence'],
]

/** Nodes with no live backend counterpart yet — panel says so honestly. */
const DEMO_NODE_IDS = new Set(['governance', 'assurance', 'evidence'])

const STATUS_COLOR: Record<string, string> = {
  up: '#34d399',
  degraded: '#fbbf24',
  down: '#f87171',
  unknown: '#60a5fa',
}

function nodeById(id: string) {
  return NODES.find((n) => n.id === id)!
}

function findComponent(components: ComponentStatus[], name?: string) {
  if (!name) return undefined
  return components.find((c) => c.name === name)
}

interface KcnCoreGraphProps {
  components: ComponentStatus[]
  loading: boolean
}

export default function KcnCoreGraph({ components, loading }: KcnCoreGraphProps) {
  const [selected, setSelected] = useState<string | null>(null)

  const selectedNode = selected ? nodeById(selected) : null
  const selectedComponent = selectedNode ? findComponent(components, selectedNode.componentName) : undefined

  // "Camera fly to node" — purely CSS: scale + translate the whole graph
  // toward the clicked node's coordinates.
  const focusTransform = selectedNode
    ? {
        transform: `scale(1.6) translate(${400 - selectedNode.x}px, ${300 - selectedNode.y}px)`,
        transformOrigin: `${selectedNode.x}px ${selectedNode.y}px`,
      }
    : { transform: 'scale(1) translate(0, 0)', transformOrigin: '400px 300px' }

  return (
    <div style={{ position: 'relative' }}>
      <div
        style={{
          overflow: 'hidden',
          borderRadius: 16,
          background: 'radial-gradient(ellipse at 50% 40%, #0b1226 0%, #05070f 75%)',
          border: '1px solid rgba(120,160,255,0.18)',
          boxShadow: '0 0 60px rgba(30,80,255,0.12) inset',
        }}
      >
        <svg
          viewBox="0 0 800 600"
          role="img"
          aria-label="KCN ecosystem diagram"
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
            transition: 'transform 0.8s cubic-bezier(0.22, 1, 0.36, 1)',
            ...focusTransform,
          }}
        >
          <defs>
            <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#93c5fd" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#93c5fd" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Edges — animated flowing dash to suggest live data movement */}
          {EDGES.map(([fromId, toId]) => {
            const from = nodeById(fromId)
            const to = nodeById(toId)
            return (
              <line
                key={`${fromId}-${toId}`}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke="rgba(120,160,255,0.35)"
                strokeWidth={2}
                strokeDasharray="6 6"
                style={{ animation: 'kcn-flow 3s linear infinite' }}
              />
            )
          })}

          {/* Core glow halo */}
          <circle cx={400} cy={380} r={90} fill="url(#coreGlow)" style={{ animation: 'kcn-pulse 3.2s ease-in-out infinite' }} />

          {/* Nodes */}
          {NODES.map((node) => {
            const component = findComponent(components, node.componentName)
            const colorKey = loading ? 'unknown' : component ? component.status : 'unknown'
            const color = STATUS_COLOR[colorKey]
            const isSelected = selected === node.id

            return (
              <g
                key={node.id}
                onClick={() => setSelected(node.id)}
                style={{ cursor: 'pointer' }}
                role="button"
                aria-label={`Inspect ${node.label}`}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') setSelected(node.id)
                }}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.radius}
                  fill="rgba(8,12,28,0.9)"
                  stroke={color}
                  strokeWidth={isSelected ? 4 : 2}
                  style={
                    node.id === 'core'
                      ? { animation: 'kcn-pulse 2.4s ease-in-out infinite' }
                      : undefined
                  }
                />
                <circle cx={node.x} cy={node.y} r={4} fill={color} />
                <text
                  x={node.x}
                  y={node.y + node.radius + 18}
                  textAnchor="middle"
                  fill="#e2e8f0"
                  fontSize={12}
                  fontWeight={700}
                  letterSpacing="0.04em"
                >
                  {node.label}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {selectedNode && (
        <div
          role="dialog"
          aria-label={`${selectedNode.label} detail panel`}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            width: 260,
            background: 'rgba(8,12,28,0.92)',
            border: '1px solid rgba(120,160,255,0.3)',
            borderRadius: 12,
            padding: '1rem 1.1rem',
            color: '#e2e8f0',
            backdropFilter: 'blur(10px)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <p style={{ fontSize: 11, letterSpacing: '0.08em', color: '#93c5fd', marginBottom: 2 }}>
                {selectedNode.sublabel.toUpperCase()}
              </p>
              <h4 style={{ fontSize: 14, fontWeight: 800, margin: 0 }}>{selectedNode.label}</h4>
            </div>
            <button
              type="button"
              onClick={() => setSelected(null)}
              aria-label="Close detail panel"
              style={{
                background: 'transparent',
                border: 'none',
                color: '#93c5fd',
                cursor: 'pointer',
                fontSize: 14,
              }}
            >
              ✕
            </button>
          </div>

          <dl style={{ marginTop: '0.75rem', fontSize: 12, lineHeight: 1.9 }}>
            {selectedComponent ? (
              <>
                <Row label="STATUS" value={selectedComponent.status.toUpperCase()} />
                {selectedComponent.detail && <Row label="DETAIL" value={selectedComponent.detail} />}
              </>
            ) : DEMO_NODE_IDS.has(selectedNode.id) ? (
              <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                Preview — this subsystem isn't wired to live telemetry yet.
              </p>
            ) : (
              <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>Waiting for readiness data…</p>
            )}
          </dl>
        </div>
      )}

      <style>{`
        @keyframes kcn-pulse {
          0%, 100% { opacity: 0.55; }
          50% { opacity: 1; }
        }
        @keyframes kcn-flow {
          to { stroke-dashoffset: -24; }
        }
      `}</style>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.5rem' }}>
      <dt style={{ color: '#94a3b8' }}>{label}</dt>
      <dd style={{ margin: 0, fontWeight: 600 }}>{value}</dd>
    </div>
  )
}
