import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { buildQueryParams, createCancellableRequest } from '../lib/api'
import type { Category } from './category'
import type { Tag } from './tag'

export type CategoryBrief = Pick<Category, 'id' | 'name' | 'icon' | 'color'>
export type TagBrief = Pick<Tag, 'id' | 'name'>

export interface ExpenseItem {
  id: number
  amount: number
  category: CategoryBrief
  tags: TagBrief[]
  transaction_time: number
  timezone_offset: number
  note: string
}

export interface ExpenseListParams {
  cursor?: number
  limit?: number
  start_time?: number
  end_time?: number
  category_id?: number
  tag_id?: number
  keyword?: string
  sort_by?: string
}

export interface ExpenseFormData {
  amount: number
  category_id: number
  tag_ids: number[]
  transaction_time: number
  timezone_offset?: number
  note?: string
}

export const useExpenseStore = defineStore('expense', () => {
  // Active expenses (used by HomePage, ExpenseListPage)
  const items = ref<ExpenseItem[]>([])
  const nextCursor = ref<number>()
  const total = ref(0)
  const loading = ref(false)
  const hasMore = ref(true)

  // Deleted expenses (used by TrashPage) — separate array to avoid cross-page contamination
  const deletedItems = ref<ExpenseItem[]>([])
  const deletedTotal = ref(0)
  const deletedLoading = ref(false)

  // Request cancellation for list fetches
  const listRequest = createCancellableRequest()
  let fetchSeq = 0

  async function fetchList(params: ExpenseListParams = {}, append = false) {
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

        const res = await api.get('/v1/expenses', { params: query, signal })
        return res.data
      })

      // Stale response — a newer fetch superseded us
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
      // Only clear loading if we are the latest fetch
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

  async function getOne(id: number): Promise<ExpenseItem> {
    const res = await api.get(`/v1/expenses/${id}`)
    return res.data
  }

  async function create(data: ExpenseFormData) {
    const res = await api.post('/v1/expenses', data)
    return res.data
  }

  async function updateExpense(id: number, data: Partial<ExpenseFormData>) {
    const res = await api.put(`/v1/expenses/${id}`, data)
    return res.data
  }

  async function remove(id: number) {
    await api.delete(`/v1/expenses/${id}`)
    items.value = items.value.filter((e) => e.id !== id)
    total.value--
  }

  async function fetchDeleted() {
    deletedLoading.value = true
    try {
      const res = await api.get('/v1/expenses', { params: { deleted: 1, limit: 100 } })
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
    await api.post(`/v1/expenses/${id}/restore`)
    deletedItems.value = deletedItems.value.filter((e) => e.id !== id)
    deletedTotal.value--
  }

  async function batchPermanentDelete(ids: number[]) {
    await api.post('/v1/expenses/batch-delete', { ids })
    deletedItems.value = deletedItems.value.filter((e) => !ids.includes(e.id))
    deletedTotal.value -= ids.length
  }

  return {
    items, nextCursor, total, loading, hasMore,
    deletedItems, deletedTotal, deletedLoading,
    fetchList, resetList, getOne, create, updateExpense, remove,
    fetchDeleted, resetDeleted, restore, batchPermanentDelete,
  }
})
