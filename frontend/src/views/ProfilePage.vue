<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showDialog } from 'vant'
import { withMutate } from '../lib/feedback'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const showNicknameEdit = ref(false)
const nickname = ref('')
const submitting = ref(false)

onMounted(async () => {
  if (!auth.user) {
    await auth.fetchProfile()
  }
  nickname.value = auth.user?.nickname || ''
})

async function saveNickname() {
  submitting.value = true
  await withMutate(
    async () => {
      await auth.updateProfile({ nickname: nickname.value })
      showNicknameEdit.value = false
    },
    '昵称修改成功',
    '修改失败',
  )
  submitting.value = false
}

async function handleLogout() {
  try {
    await showDialog({
      title: '退出登录',
      message: '确定要退出吗？',
    })
    await auth.logout()
    router.push('/login')
  } catch {
    // cancelled
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="我的" />

    <div class="profile-header">
      <div class="profile-avatar">
        {{ (auth.user?.nickname || auth.user?.username || '?')[0] }}
      </div>
      <div class="profile-name">
        {{ auth.user?.nickname || auth.user?.username }}
      </div>
      <div class="profile-username">@{{ auth.user?.username }}</div>
    </div>

    <van-cell-group inset>
      <van-cell title="修改昵称" is-link @click="showNicknameEdit = true" />
      <van-cell title="修改PIN码" is-link @click="router.push('/pin-change')" />
      <van-cell title="分类管理" is-link to="/categories" data-testid="profile-nav-categories" />
      <van-cell title="标签管理" is-link to="/tags" data-testid="profile-nav-tags" />
      <van-cell title="回收站" is-link to="/trash" />
    </van-cell-group>

    <div class="profile-logout">
      <van-button round block type="danger" data-testid="profile-logout" @click="handleLogout">
        退出登录
      </van-button>
    </div>

    <van-dialog
      v-model:show="showNicknameEdit"
      title="修改昵称"
      show-cancel-button
      :confirm-button-disabled="submitting"
      @confirm="saveNickname"
    >
      <div class="profile-dialog-body">
        <van-field v-model="nickname" label="昵称" placeholder="输入新昵称" />
      </div>
    </van-dialog>
  </div>
</template>

<style scoped>
.profile-header {
  text-align: center;
  padding: var(--space-2xl) 0 var(--space-xl);
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--color-surface);
}

.profile-name {
  margin-top: var(--space-md);
  font-size: 18px;
  font-weight: 500;
}

.profile-username {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.profile-logout {
  padding: var(--space-2xl) var(--space-lg);
}

.profile-dialog-body {
  padding: var(--space-md) var(--space-lg);
}
</style>
