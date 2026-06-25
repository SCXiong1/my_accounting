import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { buildQueryParams, createCancellableRequest } from '../lib/api'
import { TRASH_PAGE_LIMIT } from '../core/constants'
import type { Category } from './category'
import type { Tag } from './tag'

export type CategoryBrief = Pick<Category, 'id' | 'name' | 'icon' | 'color'>
export type TagBrief = Pick<Tag, 'id' | 'name'>

export interface TransactionItem {
  id: number
  amount: number
  category: CategoryBrief
  tags: TagBrief[]
  transaction_time: number
  timezone_offset: number
  note: string
  type: string
}

export interface TransactionListParams {
  cursor?: number
  limit?: number
  start_time?: number
  end_time?: number
  category_id?: number
  tag_id?: number
  keyword?: string
  sort_by?: string
}

export interface TransactionFormData {
  amount: number
  category_id: number
  tag_ids: number[]
  transaction_time: number
  timezone_offset?: number
  note?: string
  type?: string
}

export const useTransactionStore = defineStore('transaction', () => {
  const items = ref<TransactionItem[]>([])
  const nextCursor = ref<number>()
  const total = ref(0)
  const loading = ref(false)
  const hasMore = ref(true)

  const deletedItems = ref<TransactionItem[]>([])
  const deletedTotal = ref(0)
  const deletedLoading = ref(false)

  const listRequest = createCancellableRequest()
  let fetchSeq = 0

  async function fetchList(params: TransactionListParams = {}, append = false) {
    const mySeq = ++fetchSeq
    loading.value = true
    try {
      const data = await listRequest.execute(async (signal) => {
        const query = buildQueryParams({
          limit: params.limit,
          cursor: params.cursor,
          start_time: params.start_time,
          end_time: params.end_time,
          category_id: params.category_id,
          tag_id: params.tag_id,
          keyword: params.keyword,
          sort_by: params.sort_by,
        })

        const res = await api.get('/v1/transactions', { params: query, signal })
        return res.data
      })

      if (mySeq !== fetchSeq) return undefined

      if (append) {
        items.value.push(...data.items)
      } else {
        items.value = data.items
      }
      nextCursor.value = data.next_cursor
      total.value = data.total
      hasMore.value = data.next_cursor !== null
      return data
    } finally {
      if (mySeq === fetchSeq) {
        loading.value = false
      }
    }
  }

  function resetList() {
    items.value = []
    nextCursor.value = undefined
    total.value = 0
    hasMore.value = true
  }

  async function getOne(id: number): Promise<TransactionItem> {
    const res = await api.get(`/v1/transactions/${id}`)
    return res.data
  }

  async function create(data: TransactionFormData) {
    const res = await api.post('/v1/transactions', data)
    return res.data
  }

  async function updateTransaction(id: number, data: Partial<TransactionFormData>) {
    const res = await api.put(`/v1/transactions/${id}`, data)
    return res.data
  }

  async function remove(id: number) {
    await api.delete(`/v1/transactions/${id}`)
    items.value = items.value.filter((e) => e.id !== id)
    total.value--
  }

  async function fetchDeleted() {
    deletedLoading.value = true
    try {
      const res = await api.get('/v1/transactions', {
        params: { deleted: 1, limit: TRASH_PAGE_LIMIT },
      })
      deletedItems.value = res.data.items
      deletedTotal.value = res.data.total
    } finally {
      deletedLoading.value = false
    }
  }

  function resetDeleted() {
    deletedItems.value = []
    deletedTotal.value = 0
  }

  async function restore(id: number) {
    await api.post(`/v1/transactions/${id}/restore`)
    deletedItems.value = deletedItems.value.filter((e) => e.id !== id)
    deletedTotal.value--
  }

  async function batchPermanentDelete(ids: number[]) {
    const res = await api.post('/v1/transactions/batch-delete', { ids })
    const deletedCount = res.data.deleted_count ?? ids.length
    deletedItems.value = deletedItems.value.filter((e) => !ids.includes(e.id))
    deletedTotal.value = Math.max(0, deletedTotal.value - deletedCount)
  }

  return {
    items,
    nextCursor,
    total,
    loading,
    hasMore,
    deletedItems,
    deletedTotal,
    deletedLoading,
    fetchList,
    resetList,
    getOne,
    create,
    updateTransaction,
    remove,
    fetchDeleted,
    resetDeleted,
    restore,
    batchPermanentDelete,
  }
})
