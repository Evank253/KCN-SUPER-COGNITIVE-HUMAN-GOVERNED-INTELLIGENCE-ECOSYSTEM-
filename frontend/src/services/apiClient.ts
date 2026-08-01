/** Base API service — wraps axios with base URL and auth headers. */

import axios, { type AxiosInstance } from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Attach stored access token to every request
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = ['Bearer', token].join(' ')
    }
    return config
  })

  return client
}

export const apiClient = createApiClient()
