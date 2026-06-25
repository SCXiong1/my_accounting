import { shallowRef } from 'vue'
import { defineStore } from 'pinia'
import api from '../lib/api'

interface CrudItem {
  id: number
  display_order?: number
}

export function createCrudStore<T extends CrudItem>(config: { name: string; endpoint: string }) {
  return defineStore(config.name, () => {
    const list = shallowRef<T[]>([])
    const loading = shallowRef(false)

    async function fetchList() {
      loading.value = true
      try {
        const res = await api.get<T[]>(config.endpoint)
        list.value = res.data
      } finally {
        loading.value = false
      }
    }

    async function create(data: Partial<T>) {
      const res = await api.post<T>(config.endpoint, data)
      list.value = [...list.value, res.data]
      return res.data
    }

    async function update(id: number, data: Partial<T>) {
      const res = await api.put<T>(`${config.endpoint}/${id}`, data)
      list.value = list.value.map((item) => (item.id === id ? res.data : item))
      return res.data
    }

    async function remove(id: number) {
      await api.delete(`${config.endpoint}/${id}`)
      list.value = list.value.filter((item) => item.id !== id)
    }

    async function sort(orders: { id: number; display_order: number }[]) {
      await api.put(`${config.endpoint}/sort`, { orders })
      await fetchList()
    }

    return { list, loading, fetchList, create, update, remove, sort }
  })
}
