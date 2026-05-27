import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export interface Tag {
  id: number
  name: string
  display_order: number
  expense_count: number
}

export const useTagStore = defineStore('tag', () => {
  const list = ref<Tag[]>([])

  async function fetchList() {
    const res = await api.get('/v1/tags')
    list.value = res.data
  }

  async function create(name: string) {
    const res = await api.post('/v1/tags', { name })
    list.value.push(res.data)
    return res.data
  }

  async function update(id: number, name: string) {
    const res = await api.put(`/v1/tags/${id}`, { name })
    const idx = list.value.findIndex(t => t.id === id)
    if (idx !== -1) Object.assign(list.value[idx], res.data)
  }

  async function remove(id: number) {
    await api.delete(`/v1/tags/${id}`)
    list.value = list.value.filter(t => t.id !== id)
  }

  async function sort(orders: { id: number; display_order: number }[]) {
    await api.put('/v1/tags/sort', { orders })
    await fetchList()
  }

  return { list, fetchList, create, update, remove, sort }
})
