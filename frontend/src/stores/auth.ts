import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../lib/api'

export interface User {
  id: number
  username: string
  nickname: string
  pin_changed: boolean
  created_at: number
  updated_at: number
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  const mustChangePin = computed(() => user.value?.pin_changed === false)

  async function login(username: string, pin: string) {
    const res = await api.post('/auth/login', { username, pin })
    user.value = res.data.user
  }

  async function fetchProfile() {
    const res = await api.get('/v1/user/profile')
    user.value = res.data.user
  }

  async function updateProfile(data: { nickname?: string }) {
    const res = await api.put('/v1/user/profile', data)
    user.value = res.data.user
  }

  async function changePin(currentPin: string, newPin: string) {
    await api.post('/auth/change-pin', {
      current_pin: currentPin,
      new_pin: newPin,
    })
    if (user.value) {
      user.value.pin_changed = true
    }
  }

  async function verifySecurity(username: string, answer: string) {
    await api.post('/auth/verify-security', { username, answer })
  }

  async function resetPin(username: string, answer: string, newPin: string) {
    await api.post('/auth/reset-pin', {
      username,
      answer,
      new_pin: newPin,
    })
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } finally {
      user.value = null
    }
  }

  return {
    user,
    mustChangePin,
    login,
    fetchProfile,
    updateProfile,
    changePin,
    verifySecurity,
    resetPin,
    logout,
  }
})
