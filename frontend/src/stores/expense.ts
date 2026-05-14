import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export interface CategoryBrief {
  id: number
  name: string
  icon: string
  color: string
}

export interface TagBrief {
  id: number
  name: string
}

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
  cursor?: number | null
  limit?: number
  start_time?: number | null
  end_time?: number | null
  category_id?: number | null
  tag_id?: number | null
  keyword?: string | null
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
  const items = ref<ExpenseItem[]>([])
  const nextCursor = ref<number | null>(null)
  const total = ref(0)
  const loading = ref(false)
  const hasMore = ref(true)

  async function fetchList(params: ExpenseListParams = {}, append = false) {
    loading.value = true
    try {
      const query: Record<string, string> = {}
      if (params.limit) query.limit = String(params.limit)
      if (params.cursor) query.cursor = String(params.cursor)
      if (params.start_time) query.start_time = String(params.start_time)
      if (params.end_time) query.end_time = String(params.end_time)
      if (params.category_id) query.category_id = String(params.category_id)
      if (params.tag_id) query.tag_id = String(params.tag_id)
      if (params.keyword) query.keyword = params.keyword
      if (params.sort_by) query.sort_by = params.sort_by

      const res = await api.get('/v1/expenses', { params: query })
      const data = res.data

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
      loading.value = false
    }
  }

  function resetList() {
    items.value = []
    nextCursor.value = null
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
    loading.value = true
    try {
      const res = await api.get('/v1/expenses', { params: { deleted: 1, limit: 100 } })
      items.value = res.data.items
      total.value = res.data.total
      hasMore.value = false
    } finally {
      loading.value = false
    }
  }

  async function restore(id: number) {
    await api.post(`/v1/expenses/${id}/restore`)
    items.value = items.value.filter((e) => e.id !== id)
    total.value--
  }

  return { items, nextCursor, total, loading, hasMore, fetchList, resetList, getOne, create, updateExpense, remove, fetchDeleted, restore }
})
