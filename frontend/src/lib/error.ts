import axios from 'axios'

/** 从请求错误中提取可读的错误信息 */
export function getErrorMessage(e: unknown, fallback = '操作失败'): string {
  if (axios.isAxiosError(e)) {
    const detail = e.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string; loc?: string[] }
      return first.msg || fallback
    }
    if (!e.response) return '网络连接失败，请检查网络'
  }
  return fallback
}
