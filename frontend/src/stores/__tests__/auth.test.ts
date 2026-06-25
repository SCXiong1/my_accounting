import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

vi.mock('../../lib/api', () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: {} }),
    get: vi.fn().mockResolvedValue({ data: { user: null } }),
    put: vi.fn().mockResolvedValue({ data: { user: null } }),
  },
}))

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('logout', () => {
    it('清除 user 状态', async () => {
      const store = useAuthStore()
      store.$patch({
        user: { id: 1, username: 'test', nickname: 'Test', pin_changed: true, created_at: 0, updated_at: 0 },
      })

      await store.logout()

      expect(store.user).toBeNull()
    })

    it('不依赖 Router，可独立调用', async () => {
      const store = useAuthStore()
      await expect(store.logout()).resolves.not.toThrow()
    })
  })

  describe('mustChangePin', () => {
    it('当 pin_changed 为 false 时返回 true', () => {
      const store = useAuthStore()
      store.$patch({
        user: { id: 1, username: 'test', nickname: 'Test', pin_changed: false, created_at: 0, updated_at: 0 },
      })

      expect(store.mustChangePin).toBe(true)
    })

    it('当 pin_changed 为 true 时返回 false', () => {
      const store = useAuthStore()
      store.$patch({
        user: { id: 1, username: 'test', nickname: 'Test', pin_changed: true, created_at: 0, updated_at: 0 },
      })

      expect(store.mustChangePin).toBe(false)
    })

    it('当 user 为 null 时返回 false', () => {
      const store = useAuthStore()
      expect(store.mustChangePin).toBe(false)
    })
  })
})
