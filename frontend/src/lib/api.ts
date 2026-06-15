import axios, { type AxiosRequestConfig } from 'axios'
import { getToken, removeToken } from './token'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动附加 JWT
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 处理器（可由 Vue Router 注入）
let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler
}

// 响应拦截器：处理 401 跳转
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken()
      const path = window.location.pathname
      if (path !== '/login' && path !== '/register') {
        if (onUnauthorized) {
          onUnauthorized()
        } else {
          window.location.href = '/login'
        }
      }
    }
    // 不在这里显示 toast，由各页面自行处理错误反馈
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

// Request cancellation support — guards against stale finally blocks
export function createCancellableRequest() {
  let abortController: AbortController | null = null
  let requestId = 0

  function cancel() {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
  }

  async function execute<T>(requestFn: (signal: AbortSignal) => Promise<T>): Promise<T> {
    cancel()
    const thisId = ++requestId
    abortController = new AbortController()
    try {
      return await requestFn(abortController.signal)
    } finally {
      // Only clean up if we are still the active request.
      // An older request's finally must not clobber the new one.
      if (requestId === thisId) {
        abortController = null
      }
    }
  }

  return { cancel, execute }
}

export default api
