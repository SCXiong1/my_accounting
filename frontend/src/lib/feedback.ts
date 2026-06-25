import { reactive } from 'vue'
import { getErrorMessage } from './error'
import { TOAST_DURATION_MS } from '../core/constants'

export interface NotifyItem {
  id: number
  type: 'success' | 'error' | 'tip'
  message: string
}

let nextId = 0
export const notifyState = reactive<{ items: NotifyItem[] }>({ items: [] })

function add(type: NotifyItem['type'], message: string) {
  const id = ++nextId
  notifyState.items.push({ id, type, message })
  setTimeout(() => remove(id), TOAST_DURATION_MS)
}

export function remove(id: number) {
  const idx = notifyState.items.findIndex((n) => n.id === id)
  if (idx >= 0) {
    notifyState.items.splice(idx, 1)
  }
}

export function showSuccess(msg: string) {
  add('success', msg)
}
export function showError(msg: string) {
  add('error', msg)
}
export function showTip(msg: string) {
  add('tip', msg)
}

export async function withMutate(
  fn: () => Promise<void>,
  successMsg: string,
  fallbackMsg: string,
): Promise<void> {
  try {
    await fn()
    showSuccess(successMsg)
  } catch (e: unknown) {
    showError(getErrorMessage(e, fallbackMsg))
  }
}
