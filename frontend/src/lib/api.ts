import axios from 'axios'
import { API_TIMEOUT_MS } from '../core/constants'

const api = axios.create({
  baseURL: '/api',
  timeout: API_TIMEOUT_MS,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      if (path !== '/login' && path !== '/pin-change') {
        if (onUnauthorized) {
          onUnauthorized()
        } else {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

export function buildQueryParams(obj: Record<string, unknown>): Record<string, string> {
  const params: Record<string, string> = {}
  for (const [key, value] of Object.entries(obj)) {
    if (value !== undefined && value !== null) {
      params[key] = String(value)
    }
  }
  return params
}

export function createCancellableRequest() {
  let abortController: AbortController | null = null
  let requestId = 0
  const cancelledSet = new WeakSet<AbortController>()

  function cancel() {
    if (abortController) {
      cancelledSet.add(abortController)
      abortController.abort()
      abortController = null
    }
  }

  async function execute<T>(
    requestFn: (signal: AbortSignal) => Promise<T>,
  ): Promise<T | undefined> {
    cancel()
    const thisId = ++requestId
    const controller = new AbortController()
    abortController = controller
    try {
      return await requestFn(controller.signal)
    } catch (e: unknown) {
      if (axios.isCancel(e) && cancelledSet.has(controller)) return undefined
      throw e
    } finally {
      if (requestId === thisId) {
        abortController = null
      }
    }
  }

  return { cancel, execute }
}

export default api
