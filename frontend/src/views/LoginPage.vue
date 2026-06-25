<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../lib/error'
import { showSuccess, showError, showTip, withMutate } from '../lib/feedback'
import { LOGIN_REDIRECT_DELAY_MS, PIN_MIN_LENGTH, PIN_MAX_LENGTH } from '../core/constants'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const pin = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !pin.value) {
    showTip('请填写用户名和PIN码')
    return
  }
  if (pin.value.length < PIN_MIN_LENGTH || pin.value.length > PIN_MAX_LENGTH) {
    showTip(`PIN码需要${PIN_MIN_LENGTH}-${PIN_MAX_LENGTH}位数字`)
    return
  }
  loading.value = true
  await withMutate(
    async () => {
      await auth.login(username.value, pin.value)
      setTimeout(() => {
        if (auth.mustChangePin) {
          router.push('/pin-change')
        } else {
          router.push('/')
        }
      }, LOGIN_REDIRECT_DELAY_MS)
    },
    '登录成功',
    '登录失败',
  )
  loading.value = false
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
          v-model="pin"
          type="password"
          name="pin"
          label="PIN码"
          :placeholder="`请输入${PIN_MIN_LENGTH}-${PIN_MAX_LENGTH}位PIN码`"
          :maxlength="PIN_MAX_LENGTH"
          :rules="[
            { required: true, message: '请输入PIN码' },
            { pattern: /^\d+$/, message: 'PIN码只能包含数字' },
          ]"
          clearable
          data-testid="login-pin"
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
            class="van-button--accent"
          >
            登录
          </van-button>
        </div>
      </van-form>
      <div class="login-links">
        <router-link to="/pin-change" class="login-link"> 忘记PIN码？ </router-link>
      </div>
    </div>
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
  margin-top: var(--space-lg);
}

.login-link {
  color: var(--color-accent);
  font-size: 14px;
  cursor: pointer;
}
</style>
