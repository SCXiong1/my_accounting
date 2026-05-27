import { describe, it, expect, beforeEach } from 'vitest'
import axios from 'axios'
import { notifyState, withMutate } from '../feedback'

describe('withMutate', () => {
  beforeEach(() => {
    notifyState.items = []
  })

  it('调用 fn 成功时显示 success 通知', async () => {
    let called = false
    await withMutate(
      async () => { called = true },
      '操作成功',
      '操作失败',
    )

    expect(called).toBe(true)
    expect(notifyState.items).toHaveLength(1)
    expect(notifyState.items[0].type).toBe('success')
    expect(notifyState.items[0].message).toBe('操作成功')
  })

  it('fn 抛 axios 错误时显示错误消息', async () => {
    const axiosError = new axios.AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      { status: 400, data: { detail: '分类名称已存在' }, statusText: 'Bad Request', headers: {}, config: {} as any },
    )

    await withMutate(
      async () => { throw axiosError },
      '操作成功',
      '操作失败',
    )

    expect(notifyState.items).toHaveLength(1)
    expect(notifyState.items[0].type).toBe('error')
    expect(notifyState.items[0].message).toBe('分类名称已存在')
  })

  it('fn 抛非 axios 错误时显示 fallback 消息', async () => {
    await withMutate(
      async () => { throw new Error('something broke') },
      '操作成功',
      '备选错误消息',
    )

    expect(notifyState.items).toHaveLength(1)
    expect(notifyState.items[0].type).toBe('error')
    expect(notifyState.items[0].message).toBe('备选错误消息')
  })
})
