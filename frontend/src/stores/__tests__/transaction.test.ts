import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTransactionStore } from '../transaction'
import type { TransactionItem } from '../transaction'

// Mock the api module
vi.mock('../../lib/api', () => {
  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return {
    default: mockApi,
    buildQueryParams: (obj: Record<string, unknown>) => {
      const params: Record<string, string> = {}
      for (const [key, value] of Object.entries(obj)) {
        if (value !== undefined && value !== null) {
          params[key] = String(value)
        }
      }
      return params
    },
    createCancellableRequest: () => ({
      cancel: vi.fn(),
      execute: vi.fn(async (fn: (signal: AbortSignal) => Promise<unknown>) => fn(new AbortController().signal)),
    }),
  }
})

import api from '../../lib/api'

function makeTransaction(overrides: Partial<TransactionItem> = {}): TransactionItem {
  return {
    id: 1,
    amount: 1000,
    category: { id: 1, name: '餐饮', icon: 'food', color: '#f00' },
    tags: [],
    transaction_time: 1705276800,
    timezone_offset: -480,
    note: '午餐',
    type: 'expense',
    ...overrides,
  }
}

describe('transaction store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchList', () => {
    it('调用 API 并设置 items', async () => {
      const items = [makeTransaction({ id: 1 }), makeTransaction({ id: 2 })]
      vi.mocked(api.get).mockResolvedValue({
        data: { items, next_cursor: null, total: 2 },
      })

      const store = useTransactionStore()
      await store.fetchList()

      expect(store.items).toHaveLength(2)
      expect(store.total).toBe(2)
      expect(store.hasMore).toBe(false)
      expect(store.loading).toBe(false)
    })

    it('append 模式下追加 items', async () => {
      const store = useTransactionStore()
      store.items = [makeTransaction({ id: 1 })]

      vi.mocked(api.get).mockResolvedValue({
        data: { items: [makeTransaction({ id: 2 })], next_cursor: null, total: 2 },
      })

      await store.fetchList({}, true)

      expect(store.items).toHaveLength(2)
    })
  })

  describe('create', () => {
    it('调用 POST 并返回新记录', async () => {
      const created = makeTransaction({ id: 10 })
      vi.mocked(api.post).mockResolvedValue({ data: created })

      const store = useTransactionStore()
      const result = await store.create({
        amount: 1000,
        category_id: 1,
        tag_ids: [],
        transaction_time: 1705276800,
      })

      expect(api.post).toHaveBeenCalledWith('/v1/transactions', expect.objectContaining({
        amount: 1000,
        category_id: 1,
      }))
      expect(result).toEqual(created)
    })
  })

  describe('updateTransaction', () => {
    it('调用 PUT 并返回更新后的记录', async () => {
      const updated = makeTransaction({ id: 1, amount: 2000 })
      vi.mocked(api.put).mockResolvedValue({ data: updated })

      const store = useTransactionStore()
      const result = await store.updateTransaction(1, { amount: 2000 })

      expect(api.put).toHaveBeenCalledWith('/v1/transactions/1', { amount: 2000 })
      expect(result).toEqual(updated)
    })
  })

  describe('remove', () => {
    it('调用 DELETE 并从 items 中移除', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      const store = useTransactionStore()
      store.items = [makeTransaction({ id: 1 }), makeTransaction({ id: 2 })]
      store.total = 2

      await store.remove(1)

      expect(api.delete).toHaveBeenCalledWith('/v1/transactions/1')
      expect(store.items).toHaveLength(1)
      expect(store.items[0].id).toBe(2)
      expect(store.total).toBe(1)
    })
  })

  describe('fetchDeleted', () => {
    it('调用 API 带 deleted=1 参数', async () => {
      const items = [makeTransaction({ id: 5 })]
      vi.mocked(api.get).mockResolvedValue({
        data: { items, total: 1 },
      })

      const store = useTransactionStore()
      await store.fetchDeleted()

      expect(api.get).toHaveBeenCalledWith('/v1/transactions', {
        params: { deleted: 1, limit: 100 },
      })
      expect(store.deletedItems).toEqual(items)
      expect(store.deletedTotal).toBe(1)
    })
  })

  describe('restore', () => {
    it('调用 restore API 并从 deletedItems 移除', async () => {
      vi.mocked(api.post).mockResolvedValue({})

      const store = useTransactionStore()
      store.deletedItems = [makeTransaction({ id: 5 })]
      store.deletedTotal = 1

      await store.restore(5)

      expect(api.post).toHaveBeenCalledWith('/v1/transactions/5/restore')
      expect(store.deletedItems).toHaveLength(0)
      expect(store.deletedTotal).toBe(0)
    })
  })

  describe('batchPermanentDelete', () => {
    it('调用 batch-delete API 并更新 deletedItems', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: { deleted_count: 2 } })

      const store = useTransactionStore()
      store.deletedItems = [
        makeTransaction({ id: 1 }),
        makeTransaction({ id: 2 }),
        makeTransaction({ id: 3 }),
      ]
      store.deletedTotal = 3

      await store.batchPermanentDelete([1, 2])

      expect(api.post).toHaveBeenCalledWith('/v1/transactions/batch-delete', { ids: [1, 2] })
      expect(store.deletedItems).toHaveLength(1)
      expect(store.deletedItems[0].id).toBe(3)
      expect(store.deletedTotal).toBe(1)
    })
  })

  describe('resetList', () => {
    it('重置列表状态', () => {
      const store = useTransactionStore()
      store.items = [makeTransaction()]
      store.total = 1
      store.hasMore = false

      store.resetList()

      expect(store.items).toEqual([])
      expect(store.total).toBe(0)
      expect(store.hasMore).toBe(true)
    })
  })
})
