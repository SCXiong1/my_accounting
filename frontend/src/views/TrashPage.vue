<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import { useTransactionStore } from '../stores/transaction'
import { showError, withMutate } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import TransactionCard from '../components/TransactionCard.vue'

const store = useTransactionStore()
const restoring = ref<number | null>(null)

const selectMode = ref(false)
const selectedIds = ref<number[]>([])

const allSelected = computed(
  () => store.deletedItems.length > 0 && selectedIds.value.length === store.deletedItems.length,
)

function toggleSelectMode() {
  selectMode.value = !selectMode.value
  if (!selectMode.value) {
    selectedIds.value = []
  }
}

function toggleSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = store.deletedItems.map((e) => e.id)
  }
}

onMounted(() => {
  loadDeleted()
})

async function loadDeleted() {
  store.resetDeleted()
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
      await store.restore(id)
    },
    '已恢复',
    '恢复失败',
  )
  restoring.value = null
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await showConfirmDialog({
      title: '永久删除',
      message: `确定永久删除 ${selectedIds.value.length} 条记录吗？此操作不可撤销。`,
    })
  } catch {
    return
  }
  await withMutate(
    async () => {
      await store.batchPermanentDelete(selectedIds.value)
      selectedIds.value = []
      selectMode.value = false
    },
    '已删除',
    '删除失败',
  )
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="回收站" left-text="返回" left-arrow @click-left="$router.back()">
      <template #right>
        <van-button
          size="small"
          type="primary"
          plain
          data-testid="trash-select-mode"
          @click="toggleSelectMode"
        >
          {{ selectMode ? '取消' : '批量删除' }}
        </van-button>
      </template>
    </van-nav-bar>

    <div v-if="store.deletedItems.length === 0 && !store.deletedLoading" class="empty-placeholder">
      <div class="trash-empty-icon">🗑️</div>
      <div class="trash-empty-text">回收站是空的</div>
      <div class="trash-empty-hint">删除的支出会保留在这里，可以恢复</div>
    </div>

    <div v-for="transaction in store.deletedItems" :key="transaction.id" class="trash-item">
      <van-checkbox
        v-if="selectMode"
        :model-value="selectedIds.includes(transaction.id)"
        class="trash-item__checkbox"
        data-testid="trash-checkbox"
        @click="toggleSelect(transaction.id)"
      />
      <TransactionCard :transaction="transaction" class="trash-item__card" />
      <van-button
        v-if="!selectMode"
        size="small"
        type="primary"
        :loading="restoring === transaction.id"
        class="trash-item__restore"
        @click="handleRestore(transaction.id)"
      >
        恢复
      </van-button>
    </div>

    <div v-if="selectMode" class="trash-batch-bar" data-testid="trash-batch-bar">
      <van-checkbox
        :model-value="allSelected"
        data-testid="trash-select-all"
        @click="toggleSelectAll"
      >
        全选 ({{ selectedIds.length }}/{{ store.deletedItems.length }})
      </van-checkbox>
      <van-button
        type="danger"
        size="small"
        :disabled="selectedIds.length === 0"
        data-testid="trash-batch-delete"
        @click="handleBatchDelete"
      >
        删除
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

.trash-item__checkbox {
  margin-left: var(--space-md);
  flex-shrink: 0;
}

.trash-batch-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  z-index: 100;
}
</style>
