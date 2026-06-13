<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { showTip, withMutate } from '../lib/feedback'

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
  await withMutate(
    async () => {
      await auth.register(username.value, password.value, nickname.value || undefined, email.value)
      setTimeout(() => router.push('/'), 500)
    },
    '注册成功',
    '注册失败',
  )
  loading.value = false
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="注册" />
    <div class="register-form">
      <van-form @submit="handleRegister">
        <van-field v-model="username" label="用户名" placeholder="2-32 个字符" :rules="[{ required: true, message: '请输入用户名' }]" clearable data-testid="register-username" />
        <van-field v-model="email" label="邮箱" placeholder="用于找回密码" :rules="[{ required: true, message: '请输入邮箱' }]" clearable data-testid="register-hint" />
        <van-field v-model="nickname" label="昵称" placeholder="选填" clearable />
        <van-field v-model="password" type="password" label="密码" placeholder="至少 6 位" :rules="[{ required: true, message: '请输入密码' }]" clearable data-testid="register-password" />
        <van-field v-model="password2" type="password" label="确认密码" placeholder="再次输入密码" :rules="[{ required: true, message: '请确认密码' }]" clearable data-testid="register-password-confirm" />
        <div class="register-actions">
          <van-button round block type="primary" native-type="submit" :loading="loading" loading-text="注册中..." data-testid="register-submit" class="van-button--accent">注册</van-button>
        </div>
      </van-form>
      <div class="register-link">
        <router-link to="/login" class="register-link__a">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-form {
  padding: var(--space-xl) var(--space-lg) 0;
}

.register-actions {
  margin: var(--space-xl) var(--space-lg);
}

.register-link {
  text-align: center;
  margin-top: var(--space-lg);
}

.register-link__a {
  color: var(--color-accent);
  font-size: 14px;
}
</style>
