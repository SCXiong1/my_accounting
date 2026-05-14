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
    await fetchList()
    return res.data
  }

  async function update(id: number, name: string) {
    await api.put(`/v1/tags/${id}`, { name })
    await fetchList()
  }

  async function remove(id: number) {
    await api.delete(`/v1/tags/${id}`)
    await fetchList()
  }

  async function sort(orders: { id: number; display_order: number }[]) {
    await api.put('/v1/tags/sort', { orders })
    await fetchList()
  }

  return { list, fetchList, create, update, remove, sort }
})
