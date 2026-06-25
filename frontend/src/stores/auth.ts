import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'
import { setToken, removeToken, getToken } from '../lib/token'

export interface User {
  id: number
  username: string
  nickname: string
  created_at: number
  updated_at: number
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(getToken())
  async function register(
    username: string,
    password: string,
    nickname: string | undefined,
    email: string,
  ) {
    const res = await api.post('/auth/register', { username, email, password, nickname })
    token.value = res.data.token
    user.value = res.data.user
    setToken(res.data.token)
  }

  async function login(username: string, password: string) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.token
    user.value = res.data.user
    setToken(res.data.token)
  }

  async function fetchProfile() {
    const res = await api.get('/v1/user/profile')
    user.value = res.data.user
  }

  async function updateProfile(data: {
    nickname?: string
    password?: string
    old_password?: string
  }) {
    const res = await api.put('/v1/user/profile', data)
    user.value = res.data.user
    if (res.data.token) {
      token.value = res.data.token
      setToken(res.data.token)
    }
  }

  async function forgotPassword(username: string, email: string, newPassword: string) {
    const res = await api.post('/auth/forgot-password', {
      username,
      email,
      new_password: newPassword,
    })
    return res.data.message as string
  }

  function logout() {
    user.value = null
    token.value = null
    removeToken()
  }

  return { user, token, register, login, fetchProfile, updateProfile, forgotPassword, logout }
})
