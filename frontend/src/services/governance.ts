/** Governance API service. */

import type { ApprovalRequest, ApprovalResponse, PolicyListResponse } from '../types/api'
import { apiClient } from './apiClient'

export async function listPolicies(): Promise<PolicyListResponse> {
  const response = await apiClient.get<PolicyListResponse>('/governance/policies')
  return response.data
}

export async function submitApproval(request: ApprovalRequest): Promise<ApprovalResponse> {
  const response = await apiClient.post<ApprovalResponse>('/governance/approvals', request)
  return response.data
}
