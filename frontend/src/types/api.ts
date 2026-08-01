/** Application-wide TypeScript types. */

/** Health check response from the backend. */
export interface HealthResponse {
  status: string
  version: string
  timestamp: string
}

/** Governance policy record. */
export interface Policy {
  id: string
  name: string
  description: string
  enabled: boolean
  created_at: string
  updated_at: string
}

/** List response for governance policies. */
export interface PolicyListResponse {
  policies: Policy[]
  total: number
}

/** Approval request body. */
export interface ApprovalRequest {
  action_type: string
  description: string
  data?: Record<string, unknown>
}

/** Approval response from governance. */
export interface ApprovalResponse {
  id: string
  status: string
  created_at: string
}

/** Intelligence analysis request body. */
export interface AnalysisRequest {
  query: string
  context?: Record<string, unknown>
  module?: IntelligenceModule
}

/** Supported intelligence modules. */
export type IntelligenceModule =
  | 'research'
  | 'reasoning'
  | 'planning'
  | 'creative'
  | 'engineering'
  | 'analysis'
  | 'learning'

/** Intelligence analysis response. */
export interface AnalysisResponse {
  id: string
  module: string
  status: string
  result: Record<string, unknown> | null
  created_at: string
}

/** Authentication tokens. */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

/** API error shape. */
export interface ApiError {
  detail: string
}
