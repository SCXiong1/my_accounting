<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import { showSuccess, showError, showTip } from '../lib/feedback'
import { useTagStore, type Tag } from '../stores/tag'
import { getErrorMessage } from '../lib/error'

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
  try {
    if (editing.value) {
      await store.update(editing.value.id, tagName.value.trim())
showSuccess('修改成功')
    } else {
      await store.create(tagName.value.trim())
showSuccess('创建成功')
    }
    dialogVisible.value = false
  } catch (e: unknown) {
showError(getErrorMessage(e, '操作失败'))
  } finally {
    submitting.value = false
  }
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
  try {
    await store.remove(tag.id)
showSuccess('已删除')
  } catch (e: unknown) {
showError(getErrorMessage(e, '删除失败'))
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="标签管理" left-text="返回" left-arrow @click-left="$router.back()" />

    <div v-if="store.list.length > 0" style="padding: 12px 16px; display: flex; flex-wrap: wrap; gap: 8px;">
      <van-tag
        v-for="tag in store.list"
        :key="tag.id"
        size="large"
        closeable
        @close="handleDelete(tag)"
        @click="openEdit(tag)"
        type="primary"
        style="cursor: pointer;"
      >
        {{ tag.name }}
        <span v-if="tag.expense_count > 0" style="opacity: 0.7;"> ({{ tag.expense_count }})</span>
      </van-tag>
    </div>

    <div v-else class="empty-placeholder">
      <div style="font-size: 48px;">🏷️</div>
      <div style="margin-top: 12px;">暂无标签</div>
    </div>

    <div style="padding: 16px;">
      <van-button round block type="primary" @click="openCreate">新增标签</van-button>
    </div>

    <!-- 新增/编辑弹窗 -->
    <van-dialog
      v-model:show="dialogVisible"
      :title="editing ? '编辑标签' : '新增标签'"
      show-cancel-button
      @confirm="handleSubmit"
      :confirm-button-disabled="submitting"
    >
      <div style="padding: 12px 16px;">
        <van-field
          v-model="tagName"
          label="名称"
          placeholder="标签名称"
          :rules="[{ required: true }]"
        />
      </div>
    </van-dialog>
  </div>
</template>
