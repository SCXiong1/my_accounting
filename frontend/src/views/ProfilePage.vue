<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showDialog } from 'vant'
import { showSuccess, showError, showTip } from '../lib/feedback'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../lib/error'

const auth = useAuthStore()

const showNicknameEdit = ref(false)
const showPasswordEdit = ref(false)
const nickname = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const submitting = ref(false)

onMounted(async () => {
  if (!auth.user) {
    await auth.fetchProfile()
  }
  nickname.value = auth.user?.nickname || ''
})

async function saveNickname() {
  submitting.value = true
  try {
    await auth.updateProfile({ nickname: nickname.value })
showSuccess('昵称修改成功')
    showNicknameEdit.value = false
  } catch (e: unknown) {
showError(getErrorMessage(e, '修改失败'))
  } finally {
    submitting.value = false
  }
}

async function savePassword() {
  if (!oldPassword.value || !newPassword.value) {
showTip('请填写旧密码和新密码')
    return
  }
  submitting.value = true
  try {
    await auth.updateProfile({
      password: newPassword.value,
      old_password: oldPassword.value,
    })
showSuccess('密码修改成功')
    showPasswordEdit.value = false
  } catch (e: unknown) {
showError(getErrorMessage(e, '修改失败'))
  } finally {
    submitting.value = false
  }
}

async function handleLogout() {
  try {
    await showDialog({
      title: '退出登录',
      message: '确定要退出吗？',
    })
    auth.logout()
  } catch {
    // cancelled
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="我的" />

    <div style="text-align: center; padding: 32px 0 24px;">
      <div style="
        width: 64px; height: 64px; border-radius: 50%; background: var(--van-primary-color);
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 28px; color: #fff;
      ">
        {{ (auth.user?.nickname || auth.user?.username || '?')[0] }}
      </div>
      <div style="margin-top: 12px; font-size: 18px; font-weight: 500;">
        {{ auth.user?.nickname || auth.user?.username }}
      </div>
      <div style="font-size: 13px; color: #969799;">
        @{{ auth.user?.username }}
      </div>
    </div>

    <van-cell-group inset>
      <van-cell title="修改昵称" is-link @click="showNicknameEdit = true" />
      <van-cell title="修改密码" is-link @click="showPasswordEdit = true" />
      <van-cell title="标签管理" is-link to="/tags" />
    </van-cell-group>

    <div style="padding: 32px 16px;">
      <van-button round block type="danger" @click="handleLogout">退出登录</van-button>
    </div>

    <!-- 修改昵称 -->
    <van-dialog
      v-model:show="showNicknameEdit"
      title="修改昵称"
      show-cancel-button
      @confirm="saveNickname"
      :confirm-button-disabled="submitting"
    >
      <div style="padding: 12px 16px;">
        <van-field v-model="nickname" label="昵称" placeholder="输入新昵称" />
      </div>
    </van-dialog>

    <!-- 修改密码 -->
    <van-dialog
      v-model:show="showPasswordEdit"
      title="修改密码"
      show-cancel-button
      @confirm="savePassword"
      :confirm-button-disabled="submitting"
    >
      <div style="padding: 12px 16px;">
        <van-field v-model="oldPassword" type="password" label="旧密码" placeholder="输入旧密码" />
        <van-field v-model="newPassword" type="password" label="新密码" placeholder="至少 6 位" />
      </div>
    </van-dialog>
  </div>
</template>
