import { APIRequestContext } from '@playwright/test';
import { loadMetadata } from '../fixtures/auth.js';

const API_BASE = 'http://localhost:8080';

export async function apiClient(request: APIRequestContext) {
  const { token } = loadMetadata();
  return {
    get: (path: string) =>
      request.get(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    post: (path: string, data: unknown) =>
      request.post(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${token}` },
        data,
      }),
    put: (path: string, data: unknown) =>
      request.put(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${token}` },
        data,
      }),
    delete: (path: string) =>
      request.delete(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
  };
}
