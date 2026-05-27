<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import api from '../lib/api'
import { useExpenseStore } from '../stores/expense'
import { showSuccess, showError } from '../lib/feedback'
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
  try {
    await api.post(`/v1/expenses/${id}/restore`)
    showSuccess('已恢复')
    loadDeleted()
  } catch (e: unknown) {
    showError(getErrorMessage(e, '恢复失败'))
  } finally {
    restoring.value = null
  }
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
      <div style="font-size: 48px;">🗑️</div>
      <div style="margin-top: 12px;">回收站是空的</div>
      <div style="font-size: 12px; color: #c8c9cc; margin-top: 4px;">删除的支出会保留在这里，可以恢复</div>
    </div>

    <div v-for="expense in store.items" :key="expense.id"
      style="display: flex; align-items: center; background: #fff; border-bottom: 1px solid #f5f5f5;">
      <ExpenseCard :expense="expense" style="flex: 1;" />
      <van-button
        size="small"
        type="primary"
        :loading="restoring === expense.id"
        @click="handleRestore(expense.id)"
        style="margin-right: 12px; flex-shrink: 0;"
      >
        恢复
      </van-button>
    </div>
  </div>
</template>
