<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../lib/error'
import { showSuccess, showError, showTip, withMutate } from '../lib/feedback'
import { PIN_MIN_LENGTH, PIN_MAX_LENGTH } from '../core/constants'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const mode = computed(() => (route.query.mode === 'reset' ? 'reset' : 'change'))

const currentPin = ref('')
const newPin = ref('')
const confirmPin = ref('')
const username = ref('')
const securityAnswer = ref('')
const loading = ref(false)
const securityQuestion = ref('')

onMounted(async () => {
  if (mode.value === 'reset') {
    try {
      const res = await fetch('/api/auth/security-question')
      const data = await res.json()
      securityQuestion.value = data.question
    } catch {
      securityQuestion.value = '小1是谁？'
    }
  }
})

function validatePin(pin: string): boolean {
  return pin.length >= PIN_MIN_LENGTH && pin.length <= PIN_MAX_LENGTH && /^\d+$/.test(pin)
}

async function handleChange() {
  if (!currentPin.value || !newPin.value || !confirmPin.value) {
    showTip('请填写所有字段')
    return
  }
  if (!validatePin(newPin.value)) {
    showTip(`新PIN码需要${PIN_MIN_LENGTH}-${PIN_MAX_LENGTH}位数字`)
    return
  }
  if (newPin.value !== confirmPin.value) {
    showTip('两次输入的新PIN码不一致')
    return
  }
  if (newPin.value === currentPin.value) {
    showTip('新PIN码不能与当前PIN码相同')
    return
  }
  loading.value = true
  await withMutate(
    async () => {
      await auth.changePin(currentPin.value, newPin.value)
      setTimeout(() => router.push('/'), 500)
    },
    'PIN码修改成功',
    'PIN码修改失败',
  )
  loading.value = false
}

async function handleReset() {
  if (!username.value || !securityAnswer.value || !newPin.value || !confirmPin.value) {
    showTip('请填写所有字段')
    return
  }
  if (!validatePin(newPin.value)) {
    showTip(`新PIN码需要${PIN_MIN_LENGTH}-${PIN_MAX_LENGTH}位数字`)
    return
  }
  if (newPin.value !== confirmPin.value) {
    showTip('两次输入的新PIN码不一致')
    return
  }
  loading.value = true
  await withMutate(
    async () => {
      await auth.resetPin(username.value, securityAnswer.value, newPin.value)
      setTimeout(() => router.push('/login'), 500)
    },
    'PIN码重置成功，请重新登录',
    'PIN码重置失败',
  )
  loading.value = false
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar :title="mode === 'reset' ? '重置PIN码' : '修改PIN码'" left-arrow @click-left="router.back()" />
    <div class="pin-change-form">
      <van-form @submit="mode === 'change' ? handleChange() : handleReset()">
        <template v-if="mode === 'reset'">
          <van-field
            v-model="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
            clearable
          />
          <van-field
            v-model="securityAnswer"
            :label="securityQuestion || '安全问题'"
            placeholder="请输入答案"
            :rules="[{ required: true, message: '请输入答案' }]"
            clearable
          />
        </template>
        <template v-else>
          <van-field
            v-model="currentPin"
            type="password"
            label="当前PIN码"
            placeholder="请输入当前PIN码"
            :maxlength="PIN_MAX_LENGTH"
            :rules="[{ required: true, message: '请输入当前PIN码' }]"
            clearable
          />
        </template>
        <van-field
          v-model="newPin"
          type="password"
          label="新PIN码"
          :placeholder="`请输入${PIN_MIN_LENGTH}-${PIN_MAX_LENGTH}位新PIN码`"
          :maxlength="PIN_MAX_LENGTH"
          :rules="[
            { required: true, message: '请输入新PIN码' },
            { pattern: /^\d+$/, message: 'PIN码只能包含数字' },
          ]"
          clearable
        />
        <van-field
          v-model="confirmPin"
          type="password"
          label="确认新PIN码"
          placeholder="请再次输入新PIN码"
          :maxlength="PIN_MAX_LENGTH"
          :rules="[
            { required: true, message: '请确认新PIN码' },
            { validator: (v: string) => v === newPin, message: '两次输入的PIN码不一致' },
          ]"
          clearable
        />
        <div class="submit-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="处理中..."
            class="van-button--accent"
          >
            {{ mode === 'reset' ? '重置PIN码' : '修改PIN码' }}
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style scoped>
.pin-change-form {
  padding: var(--space-xl) var(--space-lg) 0;
}

.submit-actions {
  margin: var(--space-xl) var(--space-lg);
}
</style>
