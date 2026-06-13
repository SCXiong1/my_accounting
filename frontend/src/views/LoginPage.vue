<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../lib/error'
import { showSuccess, showError, showTip, withMutate } from '../lib/feedback'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
showTip('请填写用户名和密码')
    return
  }
  loading.value = true
  await withMutate(
    async () => {
      await auth.login(username.value, password.value)
      setTimeout(() => router.push('/'), 500)
    },
    '登录成功',
    '登录失败',
  )
  loading.value = false
}

const showForgot = ref(false)
const forgotUsername = ref('')
const forgotEmail = ref('')
const forgotNewPwd = ref('')
const forgotLoading = ref(false)

async function handleForgot() {
  if (!forgotUsername.value.trim() || !forgotEmail.value.trim() || !forgotNewPwd.value) {
showTip('请填写所有字段')
    return
  }
  if (forgotNewPwd.value.length < 6) {
showTip('新密码至少6位')
    return
  }
  forgotLoading.value = true
  try {
    await auth.forgotPassword(forgotUsername.value.trim(), forgotEmail.value.trim(), forgotNewPwd.value)
    showForgot.value = false
showSuccess('密码重置成功，请使用新密码登录')
  } catch (e: unknown) {
    showForgot.value = false
setTimeout(() => showError(getErrorMessage(e, '重置失败')), 300)
  } finally {
    forgotLoading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="登录" />
    <div class="login-form">
      <van-form @submit="handleLogin">
        <van-field
          v-model="username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
          clearable
          data-testid="login-username"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          clearable
          data-testid="login-password"
        />
        <div class="login-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="登录中..."
            data-testid="login-submit"
          >
            登录
          </van-button>
        </div>
      </van-form>
      <div class="login-links">
        <router-link to="/register" class="login-link">
          没有账号？去注册
        </router-link>
        <span class="login-link" @click="showForgot = true">
          忘记密码
        </span>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <van-dialog
      v-model:show="showForgot"
      title="重置密码"
      show-cancel-button
      @confirm="handleForgot"
      :confirm-button-disabled="forgotLoading"
      confirm-button-text="重置密码"
    >
      <div class="forgot-form">
        <van-field v-model="forgotUsername" label="用户名" placeholder="请输入你的用户名" />
        <van-field v-model="forgotEmail" label="注册邮箱" placeholder="请输入注册时的邮箱" />
        <van-field v-model="forgotNewPwd" type="password" label="新密码" placeholder="输入新密码（至少6位）" />
        <div class="forgot-hint">
          输入用户名和注册邮箱验证身份后，即可设置新密码。
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<style scoped>
.login-form {
  padding: var(--space-xl) var(--space-lg) 0;
}

.login-actions {
  margin: var(--space-xl) var(--space-lg);
}

.login-links {
  text-align: center;
  margin-top: var(--space-sm);
  display: flex;
  justify-content: space-around;
}

.login-link {
  color: var(--color-primary);
  font-size: 14px;
  cursor: pointer;
}

.forgot-form {
  padding: var(--space-md) var(--space-lg);
}

.forgot-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: var(--space-sm);
}
</style>
