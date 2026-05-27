import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export interface Category {
  id: number
  name: string
  icon: string
  color: string
  display_order: number
  expense_count: number
  total_amount: number
}

export const useCategoryStore = defineStore('category', () => {
  const list = ref<Category[]>([])

  async function fetchList() {
    const res = await api.get('/v1/categories')
    list.value = res.data
  }

  async function create(data: { name: string; icon?: string; color?: string }) {
    const res = await api.post('/v1/categories', data)
    list.value.push(res.data)
    return res.data
  }

  async function update(id: number, data: { name?: string; icon?: string; color?: string }) {
    const res = await api.put(`/v1/categories/${id}`, data)
    const idx = list.value.findIndex(c => c.id === id)
    if (idx !== -1) Object.assign(list.value[idx], res.data)
  }

  async function remove(id: number) {
    await api.delete(`/v1/categories/${id}`)
    list.value = list.value.filter(c => c.id !== id)
  }

  async function sort(orders: { id: number; display_order: number }[]) {
    await api.put('/v1/categories/sort', { orders })
    await fetchList()
  }

  return { list, fetchList, create, update, remove, sort }
})
