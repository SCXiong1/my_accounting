import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { createCrudStore } from '../createCrudStore'

// Mock the api module
vi.mock('../../lib/api', () => {
  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return { default: mockApi }
})

import api from '../../lib/api'

interface TestItem {
  id: number
  name: string
  display_order?: number
}

describe('createCrudStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('创建的 store 有正确的响应式状态', () => {
    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()

    expect(store.list).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('fetchList 调用 API 并填充 list', async () => {
    const items: TestItem[] = [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
    ]
    vi.mocked(api.get).mockResolvedValue({ data: items })

    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()

    await store.fetchList()

    expect(api.get).toHaveBeenCalledWith('/test')
    expect(store.list).toEqual(items)
    expect(store.loading).toBe(false)
  })

  it('create 调用 API 并将新项追加到 list', async () => {
    const newItem: TestItem = { id: 1, name: 'new' }
    vi.mocked(api.post).mockResolvedValue({ data: newItem })

    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()

    const result = await store.create({ name: 'new' })

    expect(api.post).toHaveBeenCalledWith('/test', { name: 'new' })
    expect(store.list).toEqual([newItem])
    expect(result).toEqual(newItem)
  })

  it('update 调用 API 并替换 list 中对应项', async () => {
    const updated: TestItem = { id: 1, name: 'updated' }
    vi.mocked(api.put).mockResolvedValue({ data: updated })

    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()
    store.list = [{ id: 1, name: 'old' }]

    const result = await store.update(1, { name: 'updated' })

    expect(api.put).toHaveBeenCalledWith('/test/1', { name: 'updated' })
    expect(store.list).toEqual([updated])
    expect(result).toEqual(updated)
  })

  it('remove 调用 API 并从 list 中移除对应项', async () => {
    vi.mocked(api.delete).mockResolvedValue({})

    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()
    store.list = [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
    ]

    await store.remove(1)

    expect(api.delete).toHaveBeenCalledWith('/test/1')
    expect(store.list).toEqual([{ id: 2, name: 'B' }])
  })

  it('sort 调用 API 并重新获取列表', async () => {
    vi.mocked(api.put).mockResolvedValue({})
    const sortedItems: TestItem[] = [
      { id: 2, name: 'B', display_order: 1 },
      { id: 1, name: 'A', display_order: 2 },
    ]
    vi.mocked(api.get).mockResolvedValue({ data: sortedItems })

    const useStore = createCrudStore<TestItem>({ name: 'test', endpoint: '/test' })
    const store = useStore()

    await store.sort([
      { id: 2, display_order: 1 },
      { id: 1, display_order: 2 },
    ])

    expect(api.put).toHaveBeenCalledWith('/test/sort', {
      orders: [
        { id: 2, display_order: 1 },
        { id: 1, display_order: 2 },
      ],
    })
    expect(api.get).toHaveBeenCalledWith('/test')
    expect(store.list).toEqual(sortedItems)
  })
})
