<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import { showTip, withMutate } from '../lib/feedback'
import { useTagStore, type Tag } from '../stores/tag'

const store = useTagStore()

const dialogVisible = ref(false)
const editing = ref<Tag | null>(null)
const tagName = ref('')
const submitting = ref(false)

onMounted(() => {
  store.fetchList()
})

function openCreate() {
  editing.value = null
  tagName.value = ''
  dialogVisible.value = true
}

function openEdit(tag: Tag) {
  editing.value = tag
  tagName.value = tag.name
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!tagName.value.trim()) {
showTip('请输入标签名称')
    return
  }
  submitting.value = true
  const isEdit = editing.value
  await withMutate(
    async () => {
      if (isEdit) {
        await store.update(editing.value!.id, tagName.value.trim())
      } else {
        await store.create(tagName.value.trim())
      }
      dialogVisible.value = false
    },
    isEdit ? '修改成功' : '创建成功',
    '操作失败',
  )
  submitting.value = false
}

async function handleDelete(tag: Tag) {
  try {
    await showConfirmDialog({
      title: '删除标签',
      message: `确定删除「${tag.name}」吗？关联的支出标签也会被清除。`,
    })
  } catch {
    return // 用户取消
  }
  await withMutate(
    () => store.remove(tag.id),
    '已删除',
    '删除失败',
  )
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="标签管理" left-text="返回" left-arrow @click-left="$router.back()" />

    <div v-if="store.list.length > 0" class="tag-list">
      <van-tag
        v-for="tag in store.list"
        :key="tag.id"
        size="large"
        closeable
        data-testid="tag-manage-tag"
        @close="handleDelete(tag)"
        @click="openEdit(tag)"
        type="primary"
        class="tag-list__item"
      >
        {{ tag.name }}
        <span v-if="tag.expense_count > 0" class="tag-list__count"> ({{ tag.expense_count }})</span>
      </van-tag>
    </div>

    <div v-else class="empty-placeholder">
      <div class="tag-empty-icon">🏷️</div>
      <div class="tag-empty-text">暂无标签</div>
    </div>

    <div class="tag-add-btn">
      <van-button round block type="primary" data-testid="tag-manage-add-btn" @click="openCreate">新增标签</van-button>
    </div>

    <!-- 新增/编辑弹窗 -->
    <van-dialog
      v-model:show="dialogVisible"
      :title="editing ? '编辑标签' : '新增标签'"
      data-testid="tag-manage-dialog"
      :show-confirm-button="false"
      show-cancel-button
    >
      <van-form @submit="handleSubmit">
        <div class="tag-dialog-body">
          <van-field
            v-model="tagName"
            label="名称"
            placeholder="标签名称"
            :rules="[{ required: true }]"
            data-testid="tag-manage-name"
          />
        </div>
      </van-form>
      <template #footer>
        <div class="van-dialog__footer">
          <van-button
            class="van-dialog__cancel van-dialog__footer-cancel"
            native-type="button"
            @click="dialogVisible = false"
          >
            取消
          </van-button>
          <van-button
            class="van-dialog__confirm van-dialog__footer-confirm"
            type="primary"
            native-type="submit"
            :loading="submitting"
            data-testid="tag-manage-confirm"
            @click="handleSubmit"
          >
            确认
          </van-button>
        </div>
      </template>
    </van-dialog>
  </div>
</template>

<style scoped>
.tag-list {
  padding: var(--space-md) var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.tag-list__item {
  cursor: pointer;
}

.tag-list__count {
  opacity: 0.7;
}

.tag-empty-icon {
  font-size: 48px;
}

.tag-empty-text {
  margin-top: var(--space-md);
}

.tag-add-btn {
  padding: var(--space-lg);
}

.tag-dialog-body {
  padding: var(--space-md) var(--space-lg);
}
</style>
