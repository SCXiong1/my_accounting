import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { setToken, getToken } from '../../lib/token'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('logout', () => {
    it('清除 user、token 和 localStorage', () => {
      // 模拟已登录状态
      setToken('fake-token')
      const store = useAuthStore()
      store.$patch({
        user: { id: 1, username: 'test', nickname: 'Test', created_at: 0, updated_at: 0 },
        token: 'fake-token',
      })

      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(getToken()).toBeNull()
    })

    it('不依赖 Router，可独立调用', () => {
      const store = useAuthStore()
      // 不抛异常即为通过
      expect(() => store.logout()).not.toThrow()
    })
  })
})
