<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import { showError, showTip, withMutate } from '../lib/feedback'
import { useCategoryStore, type Category } from '../stores/category'
import { formatAmount } from '../core/format'

const store = useCategoryStore()

const showForm = ref(false)
const editing = ref<Category | null>(null)
const formName = ref('')
const formIcon = ref('📦')
const formColor = ref('#607D8B')
const submitting = ref(false)

const iconOptions = [
  '🍽️',
  '🚗',
  '🛒',
  '🏠',
  '🎮',
  '💊',
  '📚',
  '📦',
  '🐱',
  '☕',
  '🎬',
  '✈️',
  '👕',
  '💄',
]
const colorOptions = [
  '#FF5722',
  '#2196F3',
  '#FF9800',
  '#795548',
  '#9C27B0',
  '#4CAF50',
  '#009688',
  '#607D8B',
  '#FF4081',
  '#536DFE',
]

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
  const isEdit = editing.value
  await withMutate(
    async () => {
      if (isEdit) {
        await store.update(editing.value!.id, {
          name: formName.value.trim(),
          icon: formIcon.value,
          color: formColor.value,
        })
      } else {
        await store.create({
          name: formName.value.trim(),
          icon: formIcon.value,
          color: formColor.value,
        })
      }
      showForm.value = false
    },
    isEdit ? '修改成功' : '创建成功',
    '操作失败',
  )
  submitting.value = false
}

async function handleDelete(cat: Category) {
  if (cat.transaction_count > 0) {
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
  await withMutate(() => store.remove(cat.id), '已删除', '删除失败')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar
      title="分类管理"
      left-text="返回"
      left-arrow
      data-testid="category-manage-nav"
      @click-left="$router.back()"
    />

    <van-cell-group v-if="store.list.length > 0" inset class="cat-list">
      <van-swipe-cell
        v-for="cat in store.list"
        :key="cat.id"
        data-testid="category-manage-swipe-cell"
      >
        <van-cell :title="cat.name" center @click="openEdit(cat)">
          <template #icon>
            <span class="cat-list__icon">{{ cat.icon }}</span>
          </template>
          <template #label>
            <span v-if="cat.transaction_count > 0">
              {{ cat.transaction_count }} 笔 · {{ formatAmount(cat.total_amount) }}
            </span>
            <span v-else class="cat-list__empty">暂无支出</span>
          </template>
        </van-cell>
        <template #right>
          <van-button
            square
            type="danger"
            text="删除"
            data-testid="category-manage-delete-btn"
            class="cat-list__delete-btn"
            @click="handleDelete(cat)"
          />
        </template>
      </van-swipe-cell>
    </van-cell-group>

    <div v-else class="empty-placeholder">
      <div class="cat-empty-icon">📂</div>
      <div class="cat-empty-text">暂无自定义分类</div>
    </div>

    <div class="cat-add-btn">
      <van-button
        round
        block
        type="primary"
        data-testid="category-manage-add-btn"
        @click="openCreate"
      >
        新增分类
      </van-button>
    </div>

    <!-- 新增/编辑弹窗 -->
    <van-popup
      v-model:show="showForm"
      position="bottom"
      round
      :style="{ height: '60%' }"
      data-testid="category-manage-popup"
    >
      <div class="cat-popup">
        <h4 class="cat-popup__title">
          {{ editing ? '编辑分类' : '新增分类' }}
        </h4>
        <van-field
          v-model="formName"
          label="名称"
          placeholder="分类名称"
          :rules="[{ required: true }]"
          data-testid="category-manage-name"
        />
        <div class="cat-popup__section">
          <div class="cat-popup__label">图标</div>
          <div class="cat-popup__grid">
            <span
              v-for="icon in iconOptions"
              :key="icon"
              data-testid="category-manage-icon"
              class="cat-icon-option"
              :class="{ 'cat-icon-option--active': formIcon === icon }"
              @click="formIcon = icon"
              >{{ icon }}</span
            >
          </div>
        </div>
        <div class="cat-popup__section">
          <div class="cat-popup__label">颜色</div>
          <div class="cat-popup__grid">
            <span
              v-for="color in colorOptions"
              :key="color"
              data-testid="category-manage-color"
              class="cat-color-option"
              :class="{ 'cat-color-option--active': formColor === color }"
              :style="{ background: color }"
              @click="formColor = color"
            />
          </div>
        </div>
        <div class="cat-popup__save">
          <van-button
            round
            block
            type="primary"
            :loading="submitting"
            loading-text="保存中..."
            data-testid="category-manage-save"
            @click="handleSubmit"
          >
            保存
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.cat-list {
  margin-top: var(--space-md);
}

.cat-list__icon {
  font-size: 24px;
  margin-right: var(--space-md);
}

.cat-list__empty {
  color: var(--color-text-placeholder);
}

.cat-list__delete-btn {
  height: 100%;
}

.cat-empty-icon {
  font-size: 48px;
}

.cat-empty-text {
  margin-top: var(--space-md);
}

.cat-add-btn {
  padding: var(--space-lg);
}

.cat-popup {
  padding: var(--space-lg);
}

.cat-popup__title {
  margin: 0 0 var(--space-lg);
}

.cat-popup__section {
  padding: var(--space-md) var(--space-lg);
}

.cat-popup__label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

.cat-popup__grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.cat-icon-option {
  font-size: 28px;
  padding: 6px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
}

.cat-icon-option--active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.cat-color-option {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid transparent;
  cursor: pointer;
}

.cat-color-option--active {
  border-color: var(--color-primary);
}

.cat-popup__save {
  padding: var(--space-lg);
}
</style>
