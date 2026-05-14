<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../lib/error'
import { showSuccess, showError, showTip } from '../lib/feedback'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const email = ref('')
const nickname = ref('')
const password = ref('')
const password2 = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !email.value || !password.value) {
    showTip('请填写用户名、邮箱和密码')
    return
  }
  if (password.value !== password2.value) {
    showTip('两次密码不一致')
    return
  }
  loading.value = true
  try {
    await auth.register(username.value, password.value, nickname.value || undefined, email.value)
    showSuccess('注册成功')
    setTimeout(() => router.push('/'), 500)
  } catch (e: unknown) {
    showError(getErrorMessage(e, '注册失败'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="注册" />
    <div style="padding: 24px 16px 0;">
      <van-form @submit="handleRegister">
        <van-field v-model="username" label="用户名" placeholder="2-32 个字符" :rules="[{ required: true, message: '请输入用户名' }]" clearable />
        <van-field v-model="email" label="邮箱" placeholder="用于找回密码" :rules="[{ required: true, message: '请输入邮箱' }]" clearable />
        <van-field v-model="nickname" label="昵称" placeholder="选填" clearable />
        <van-field v-model="password" type="password" label="密码" placeholder="至少 6 位" :rules="[{ required: true, message: '请输入密码' }]" clearable />
        <van-field v-model="password2" type="password" label="确认密码" placeholder="再次输入密码" :rules="[{ required: true, message: '请确认密码' }]" clearable />
        <div style="margin: 24px 16px;">
          <van-button round block type="primary" native-type="submit" :loading="loading" loading-text="注册中...">注册</van-button>
        </div>
      </van-form>
      <div style="text-align: center; margin-top: 8px;">
        <router-link to="/login" style="color: var(--van-primary-color); font-size: 14px;">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>
