<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import api from '../lib/api'
import { useExpenseStore } from '../stores/expense'
import { showSuccess, showError, withMutate } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import ExpenseCard from '../components/ExpenseCard.vue'

const store = useExpenseStore()
const restoring = ref<number | null>(null)

onMounted(() => {
  loadDeleted()
})

async function loadDeleted() {
  store.resetList()
  try {
    await store.fetchDeleted()
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

async function handleRestore(id: number) {
  restoring.value = id
  await withMutate(
    async () => {
      await api.post(`/v1/expenses/${id}/restore`)
      loadDeleted()
    },
    '已恢复',
    '恢复失败',
  )
  restoring.value = null
}

async function handlePermanentDelete(id: number) {
  try {
    await showConfirmDialog({
      title: '永久删除',
      message: '此操作不可撤销，确定要永久删除吗？',
    })
  } catch {
    return
  }
  // 暂不支持永久删除，提醒用户
  showSuccess('暂不支持永久删除，恢复后重新删除即可')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="回收站" left-text="返回" left-arrow @click-left="$router.back()" />

    <div v-if="store.items.length === 0 && !store.loading" class="empty-placeholder">
      <div class="trash-empty-icon">🗑️</div>
      <div class="trash-empty-text">回收站是空的</div>
      <div class="trash-empty-hint">删除的支出会保留在这里，可以恢复</div>
    </div>

    <div v-for="expense in store.items" :key="expense.id" class="trash-item">
      <ExpenseCard :expense="expense" class="trash-item__card" />
      <van-button
        size="small"
        type="primary"
        :loading="restoring === expense.id"
        @click="handleRestore(expense.id)"
        class="trash-item__restore"
      >
        恢复
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.trash-empty-icon {
  font-size: 48px;
}

.trash-empty-text {
  margin-top: var(--space-md);
}

.trash-empty-hint {
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin-top: var(--space-xs);
}

.trash-item {
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.trash-item__card {
  flex: 1;
}

.trash-item__restore {
  margin-right: var(--space-md);
  flex-shrink: 0;
}
</style>
