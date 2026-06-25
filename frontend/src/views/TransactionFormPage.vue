<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showTip, withMutate } from '../lib/feedback'
import { useExpenseStore } from '../stores/expense'
import { useCategoryStore } from '../stores/category'
import { useTagStore } from '../stores/tag'
import { formatDate } from '../core/time'
import api from '../lib/api'
import AmountField from '../components/AmountField.vue'
import CategoryPicker from '../components/CategoryPicker.vue'
import TagCheckbox from '../components/TagCheckbox.vue'

const route = useRoute()
const router = useRouter()
const store = useExpenseStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

const isEdit = route.name === 'expenseEdit'
const expenseId = isEdit ? Number(route.params.id) : null

const amount = ref(0)
const categoryId = ref<number | null>(null)
const tagIds = ref<number[]>([])
const transactionTime = ref(Math.floor(Date.now() / 1000))
const note = ref('')
const submitting = ref(false)
const loading = ref(false)

const showDatetimePicker = ref(false)
const dateDisplay = computed(() => formatDate(transactionTime.value))

// 校验状态
const amountError = ref('')
const categoryError = ref('')

// 分类标签联动
const filteredTags = ref<{ id: number; name: string }[] | undefined>(undefined)
let prevCategoryId: number | null = null
let categoryChangeSeq = 0

async function onCategoryChange(catId: number | null) {
  if (catId === prevCategoryId) return
  prevCategoryId = catId
  tagIds.value = []
  if (catId) {
    const seq = ++categoryChangeSeq
    try {
      const res = await api.get(`/v1/categories/${catId}/tags`)
      if (seq !== categoryChangeSeq) return
      filteredTags.value = res.data
    } catch {
      if (seq !== categoryChangeSeq) return
      filteredTags.value = undefined
    }
  } else {
    filteredTags.value = undefined
  }
}

function datePickerValue() {
  const d = new Date(transactionTime.value * 1000)
  return [String(d.getFullYear()), String(d.getMonth() + 1), String(d.getDate())]
}

onMounted(async () => {
  await Promise.all([catStore.fetchList(), tagStore.fetchList()])
  if (isEdit && expenseId) {
    loading.value = true
    try {
      const expense = await store.getOne(expenseId)
      amount.value = expense.amount
      categoryId.value = expense.category.id
      prevCategoryId = expense.category.id
      tagIds.value = expense.tags.map((t) => t.id)
      transactionTime.value = expense.transaction_time
      note.value = expense.note
      // 编辑模式下加载该分类的标签，并保留已选标签
      try {
        const res = await api.get(`/v1/categories/${expense.category.id}/tags`)
        const catTags: { id: number; name: string }[] = res.data
        const existingIds = new Set(catTags.map(t => t.id))
        for (const t of expense.tags) {
          if (!existingIds.has(t.id)) {
            catTags.push({ id: t.id, name: t.name })
          }
        }
        filteredTags.value = catTags
      } catch {
        // 失败时不限制标签列表
      }
    } finally {
      loading.value = false
    }
  }
})

function onDatetimeConfirm({ selectedValues }: { selectedValues: string[] }) {
  const [y, m, d] = selectedValues.map(Number)
  const date = new Date(y, m - 1, d, 12, 0, 0)
  transactionTime.value = Math.floor(date.getTime() / 1000)
  showDatetimePicker.value = false
}

function validate(): boolean {
  let ok = true
  amountError.value = ''
  categoryError.value = ''

  if (amount.value <= 0) {
    amountError.value = '请输入金额'
    ok = false
  }
  if (!categoryId.value) {
    categoryError.value = '请选择分类'
    ok = false
  }

  if (!ok) {
showTip('请完善必填信息')
  }
  return ok
}

async function handleSubmit() {
  if (!validate()) return

  submitting.value = true
  const edit = isEdit
  await withMutate(
    async () => {
      const data = {
        amount: amount.value,
        category_id: categoryId.value as number,
        tag_ids: tagIds.value,
        transaction_time: transactionTime.value,
        note: note.value.trim(),
      }
      if (edit && expenseId) {
        await store.updateExpense(expenseId, data)
      } else {
        await store.create(data as { amount: number; category_id: number; tag_ids: number[]; transaction_time: number; note: string })
      }
      router.back()
    },
    edit ? '修改成功' : '记账成功',
    '保存失败',
  )
  submitting.value = false
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar :title="isEdit ? '编辑支出' : '新增支出'" left-text="取消" left-arrow data-testid="expense-form-nav" @click-left="$router.back()" />

    <van-loading v-if="loading" class="form-loading" />

    <div v-else class="form-body">
      <CategoryPicker v-model="categoryId" @change="onCategoryChange" />
      <div v-if="categoryError" class="form-error">{{ categoryError }}</div>

      <TagCheckbox v-model="tagIds" :filtered-tags="filteredTags" />

      <van-field
        :model-value="dateDisplay"
        is-link
        readonly
        label="日期"
        data-testid="expense-form-date"
        @click="showDatetimePicker = true"
      />

      <van-field
        v-model="note"
        label="备注"
        placeholder="写点什么..."
        autosize
        type="textarea"
        maxlength="255"
        show-word-limit
        data-testid="expense-form-note"
      />

      <AmountField v-model="amount" />
      <div v-if="amountError" class="form-error">{{ amountError }}</div>

      <div class="form-submit">
        <van-button
          round
          block
          type="primary"
          :loading="submitting"
          loading-text="保存中..."
          data-testid="expense-form-submit"
          @click="handleSubmit"
        >
          {{ isEdit ? '保存修改' : '记录支出' }}
        </van-button>
      </div>
    </div>

    <!-- 日期选择器 -->
    <van-popup v-model:show="showDatetimePicker" position="bottom" round data-testid="expense-form-date-popup">
      <van-date-picker
        title="选择日期"
:model-value="datePickerValue()"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date(2030, 11, 31)"
        @confirm="onDatetimeConfirm"
        @cancel="showDatetimePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.form-loading {
  padding: 48px;
  text-align: center;
}

.form-body {
  padding: var(--space-md) 0;
}

.form-error {
  color: var(--color-danger);
  font-size: 12px;
  padding: 0 var(--space-lg);
}

.form-submit {
  margin: var(--space-xl) var(--space-lg);
}
</style>
