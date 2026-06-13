<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showConfirmDialog } from 'vant'
import { getErrorMessage } from '../lib/error'
import { showError, withMutate } from '../lib/feedback'
import { useExpenseStore } from '../stores/expense'
import { useCategoryStore } from '../stores/category'
import { useTagStore } from '../stores/tag'
import ExpenseCard from '../components/ExpenseCard.vue'
import FilterPicker from '../components/FilterPicker.vue'

const router = useRouter()
const route = useRoute()
const store = useExpenseStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

// 筛选条件
const filterCategoryId = ref<number>()
const filterTagId = ref<number>()
const filterKeyword = ref('')
const sortBy = ref('time')

const showCategoryFilter = ref(false)
const showTagFilter = ref(false)

const INITIAL_LIMIT = 15
const PAGE_LIMIT = 10

// 下拉刷新
const refreshing = ref(false)

function syncQueryFilters() {
  const q = route.query
  filterCategoryId.value = q.category_id ? Number(q.category_id) : undefined
  filterTagId.value = q.tag_id ? Number(q.tag_id) : undefined
}

onMounted(async () => {
  syncQueryFilters()
  await Promise.all([
    store.fetchList({
      limit: INITIAL_LIMIT,
      sort_by: 'time',
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
    }),
    catStore.fetchList(),
    tagStore.fetchList(),
  ])
})

watch(() => route.query, () => {
  syncQueryFilters()
  applyFilter()
})

async function loadMore() {
  if (!store.hasMore) return
  try {
    await store.fetchList({
      cursor: store.nextCursor,
      limit: PAGE_LIMIT,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || undefined,
      sort_by: sortBy.value,
    }, true)
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

async function onRefresh() {
  refreshing.value = true
  try {
    store.resetList()
    await store.fetchList({
      limit: INITIAL_LIMIT,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || undefined,
      sort_by: sortBy.value,
    })
  } catch (e: unknown) {
    showError(getErrorMessage(e, '刷新失败'))
  } finally {
    refreshing.value = false
  }
}

async function applyFilter() {
  store.resetList()
  try {
    await store.fetchList({
      limit: INITIAL_LIMIT,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || undefined,
      sort_by: sortBy.value,
    })
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

function clearFilter() {
  filterCategoryId.value = undefined
  filterTagId.value = undefined
  filterKeyword.value = ''
}

const catColumns = computed(() => [
  { text: '全部分类', value: -1 },
  ...catStore.list.map(c => ({ text: c.name, value: c.id })),
])

const tagColumns = computed(() => [
  { text: '全部标签', value: -1 },
  ...tagStore.list.map(t => ({ text: t.name, value: t.id })),
])

function onCatSelect(val: number) {
  filterCategoryId.value = val === -1 ? undefined : val
  showCategoryFilter.value = false
  applyFilter()
}

function onTagSelect(val: number) {
  filterTagId.value = val === -1 ? undefined : val
  showTagFilter.value = false
  applyFilter()
}

function goAdd() {
  router.push('/expenses/add')
}

// 拖拽检测：左滑时抑制 click 导航
const isDragging = ref(false)
const pointerStart = ref({ x: 0, y: 0 })

function onPointerDown(e: PointerEvent) {
  pointerStart.value = { x: e.clientX, y: e.clientY }
  isDragging.value = false
}

function onPointerMove(e: PointerEvent) {
  if (Math.abs(e.clientX - pointerStart.value.x) > 10) {
    isDragging.value = true
  }
}

function onPointerUp() {
  setTimeout(() => { isDragging.value = false }, 0)
}

function goEdit(id: number) {
  if (isDragging.value) return
  router.push(`/expenses/${id}/edit`)
}

async function handleDelete(id: number) {
  try {
    await showConfirmDialog({
      title: '删除支出',
      message: '确定删除这条支出记录吗？',
    })
  } catch {
    return // 用户取消
  }
  await withMutate(
    () => store.remove(id),
    '已删除',
    '删除失败',
  )
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="支出记录" data-testid="expense-list-nav" />

    <!-- 搜索栏 -->
    <div class="expense-search-bar">
      <van-search
        v-model="filterKeyword"
        placeholder="搜索金额/分类/标签/备注..."
        shape="round"
        @search="applyFilter"
        @clear="clearFilter(); applyFilter()"
      />
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <van-tag
        class="filter-bar__item"
        :type="filterCategoryId ? 'primary' : 'default'"
        size="medium"
        @click="showCategoryFilter = true"
      >
        {{ filterCategoryId ? catStore.list.find(c => c.id === filterCategoryId)?.name : '分类' }}
      </van-tag>
      <van-tag
        class="filter-bar__item"
        :type="filterTagId ? 'primary' : 'default'"
        size="medium"
        @click="showTagFilter = true"
      >
        {{ filterTagId ? tagStore.list.find(t => t.id === filterTagId)?.name : '标签' }}
      </van-tag>
      <van-tag
        class="filter-bar__item"
        :type="sortBy === 'amount' ? 'primary' : 'default'"
        size="medium"
        @click="sortBy = sortBy === 'time' ? 'amount' : 'time'; applyFilter()"
      >
        {{ sortBy === 'time' ? '时间↓' : '金额↓' }}
      </van-tag>
      <span class="expense-total-count">
        共 {{ store.total }} 条
      </span>
    </div>

    <!-- 支出列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="store.loading"
        :finished="!store.hasMore"
        finished-text="没有更多了"
        @load="loadMore"
        :immediate-check="false"
      >
        <div v-if="store.items.length === 0 && !store.loading" class="empty-placeholder">
          <div class="expense-empty-icon">📝</div>
          <div class="expense-empty-text">暂无支出记录</div>
        </div>
        <div v-for="expense in store.items" :key="expense.id"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @click="goEdit(expense.id)">
          <van-swipe-cell data-testid="expense-list-swipe-cell">
            <ExpenseCard :expense="expense" />
            <template #right>
              <van-button
                square
                type="danger"
                text="删除"
                data-testid="expense-list-delete-btn"
@click.stop="handleDelete(expense.id)"
                class="expense-delete-btn"
              />
            </template>
          </van-swipe-cell>
          <van-divider class="expense-divider" />
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 新增按钮 -->
    <div class="expense-fab">
      <van-button
        icon="plus"
        type="primary"
        round
        size="large"
        @click="goAdd"
      />
    </div>

    <!-- 分类筛选 -->
    <FilterPicker v-model:show="showCategoryFilter" :columns="catColumns" @select="onCatSelect" />

    <!-- 标签筛选 -->
    <FilterPicker v-model:show="showTagFilter" :columns="tagColumns" @select="onTagSelect" />
  </div>
</template>

<style scoped>
.expense-search-bar {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface);
}

.expense-total-count {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 24px;
  margin-left: auto;
}

.expense-empty-icon {
  font-size: 48px;
}

.expense-empty-text {
  margin-top: var(--space-md);
}

.expense-delete-btn {
  height: 100%;
}

.expense-divider {
  margin: 0;
}

.expense-fab {
  position: fixed;
  right: var(--space-lg);
  bottom: 70px;
}
</style>
