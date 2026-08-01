/** Intelligence API service. */

import type { AnalysisRequest, AnalysisResponse } from '../types/api'
import { apiClient } from './apiClient'

export async function submitAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
  const response = await apiClient.post<AnalysisResponse>('/intelligence/analyze', request)
  return response.data
}
