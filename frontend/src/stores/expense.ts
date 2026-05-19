import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { buildQueryParams } from '../lib/api'
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
  const items = ref<ExpenseItem[]>([])
  const nextCursor = ref<number>()
  const total = ref(0)
  const loading = ref(false)
  const hasMore = ref(true)

  async function fetchList(params: ExpenseListParams = {}, append = false) {
    loading.value = true
    try {
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
