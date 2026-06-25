import { APIRequestContext } from '@playwright/test'

const API_BASE = 'http://localhost:8080'

export async function apiClient(request: APIRequestContext) {
  const loginRes = await request.post(`${API_BASE}/api/auth/login`, {
    data: { username: 'user1', pin: '1234' },
  })
  if (!loginRes.ok()) throw new Error(`apiClient login failed: ${loginRes.status()}`)

  return {
    get: (path: string) => request.get(`${API_BASE}${path}`),
    post: (path: string, data: unknown) => request.post(`${API_BASE}${path}`, { data }),
    put: (path: string, data: unknown) => request.put(`${API_BASE}${path}`, { data }),
    delete: (path: string) => request.delete(`${API_BASE}${path}`),
  }
}
