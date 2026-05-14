<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import { showSuccess, showError, showTip } from '../lib/feedback'
import { useCategoryStore, type Category } from '../stores/category'
import { formatAmount } from '../core/format'
import { getErrorMessage } from '../lib/error'

const store = useCategoryStore()

const showForm = ref(false)
const editing = ref<Category | null>(null)
const formName = ref('')
const formIcon = ref('📦')
const formColor = ref('#607D8B')
const submitting = ref(false)

const iconOptions = ['🍽️', '🚗', '🛒', '🏠', '🎮', '💊', '📚', '📦', '🐱', '☕', '🎬', '✈️', '👕', '💄']
const colorOptions = ['#FF5722', '#2196F3', '#FF9800', '#795548', '#9C27B0', '#4CAF50', '#009688', '#607D8B', '#FF4081', '#536DFE']

onMounted(() => {
  store.fetchList()
})

function openCreate() {
  editing.value = null
  formName.value = ''
  formIcon.value = '📦'
  formColor.value = '#607D8B'
  showForm.value = true
}

function openEdit(cat: Category) {
  editing.value = cat
  formName.value = cat.name
  formIcon.value = cat.icon
  formColor.value = cat.color
  showForm.value = true
}

async function handleSubmit() {
  if (!formName.value.trim()) {
showTip('请输入分类名称')
    return
  }
  submitting.value = true
  try {
    if (editing.value) {
      await store.update(editing.value.id, {
        name: formName.value.trim(),
        icon: formIcon.value,
        color: formColor.value,
      })
showSuccess('修改成功')
    } else {
      await store.create({
        name: formName.value.trim(),
        icon: formIcon.value,
        color: formColor.value,
      })
showSuccess('创建成功')
    }
    showForm.value = false
  } catch (e: unknown) {
showError(getErrorMessage(e, '操作失败'))
  } finally {
    submitting.value = false
  }
}

async function handleDelete(cat: Category) {
  if (cat.expense_count > 0) {
showError('该分类下有支出记录，无法删除')
    return
  }
  try {
    await showConfirmDialog({
      title: '删除分类',
      message: `确定删除「${cat.name}」吗？`,
    })
  } catch {
    return // 用户取消
  }
  try {
    await store.remove(cat.id)
showSuccess('已删除')
  } catch (e: unknown) {
showError(getErrorMessage(e, '删除失败'))
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="分类管理" left-text="返回" left-arrow @click-left="$router.back()" />

    <van-cell-group v-if="store.list.length > 0" inset style="margin-top: 12px;">
      <van-swipe-cell v-for="cat in store.list" :key="cat.id">
        <van-cell :title="cat.name" center @click="openEdit(cat)">
          <template #icon>
            <span style="font-size: 24px; margin-right: 12px;">{{ cat.icon }}</span>
          </template>
          <template #label>
            <span v-if="cat.expense_count > 0">
              {{ cat.expense_count }} 笔 · {{ formatAmount(cat.total_amount) }}
            </span>
            <span v-else style="color: #c8c9cc;">暂无支出</span>
          </template>
        </van-cell>
        <template #right>
          <van-button
            square
            type="danger"
            text="删除"
            @click="handleDelete(cat)"
            style="height: 100%;"
          />
        </template>
      </van-swipe-cell>
    </van-cell-group>

    <div v-else class="empty-placeholder">
      <div style="font-size: 48px;">📂</div>
      <div style="margin-top: 12px;">暂无自定义分类</div>
    </div>

    <div style="padding: 16px;">
      <van-button round block type="primary" @click="openCreate">新增分类</van-button>
    </div>

    <!-- 新增/编辑弹窗 -->
    <van-popup v-model:show="showForm" position="bottom" round :style="{ height: '60%' }">
      <div style="padding: 16px;">
        <h4 style="margin: 0 0 16px;">{{ editing ? '编辑分类' : '新增分类' }}</h4>
        <van-field
          v-model="formName"
          label="名称"
          placeholder="分类名称"
          :rules="[{ required: true }]"
        />
        <div style="padding: 12px 16px;">
          <div style="font-size: 14px; color: #646566; margin-bottom: 8px;">图标</div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <span
              v-for="icon in iconOptions"
              :key="icon"
              @click="formIcon = icon"
              :style="{
                fontSize: '28px',
                padding: '6px',
                borderRadius: '8px',
                background: formIcon === icon ? '#e8f4ff' : 'transparent',
                border: formIcon === icon ? '2px solid #1989fa' : '2px solid transparent',
                cursor: 'pointer',
              }"
            >{{ icon }}</span>
          </div>
        </div>
        <div style="padding: 12px 16px;">
          <div style="font-size: 14px; color: #646566; margin-bottom: 8px;">颜色</div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <span
              v-for="color in colorOptions"
              :key="color"
              @click="formColor = color"
              :style="{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: color,
                border: formColor === color ? '3px solid #1989fa' : '3px solid transparent',
                cursor: 'pointer',
              }"
            />
          </div>
        </div>
        <div style="padding: 16px;">
          <van-button
            round
            block
            type="primary"
            :loading="submitting"
            loading-text="保存中..."
            @click="handleSubmit"
          >
            保存
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>
