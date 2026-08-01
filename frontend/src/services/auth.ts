/** Auth API service. */

import { apiClient } from './apiClient'
import type { TokenResponse } from '../types/api'

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', {
    username,
    password,
  })
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}
