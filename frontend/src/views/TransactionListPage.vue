<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showConfirmDialog } from 'vant'
import { getErrorMessage } from '../lib/error'
import { showError, withMutate } from '../lib/feedback'
import { useTransactionStore } from '../stores/transaction'
import { useCategoryStore } from '../stores/category'
import { useTagStore } from '../stores/tag'
import TransactionCard from '../components/TransactionCard.vue'
import FilterPicker from '../components/FilterPicker.vue'
import PeriodFilterBar from '../components/PeriodFilterBar.vue'
import type { TimeRange } from '../components/PeriodFilterBar.vue'

const router = useRouter()
const route = useRoute()
const store = useTransactionStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

const timeRange = ref<TimeRange>({
  start_time: 0,
  end_time: 0,
  start_year: 0,
  start_month: 0,
  end_year: 0,
  end_month: 0,
})

const filterCategoryId = ref<number>()
const filterTagId = ref<number>()
const filterKeyword = ref('')
const sortBy = ref('time')

const showCategoryFilter = ref(false)
const showTagFilter = ref(false)

const INITIAL_LIMIT = 15
const PAGE_LIMIT = 10

function filterParams() {
  return {
    start_time: timeRange.value.start_time,
    end_time: timeRange.value.end_time,
    category_id: filterCategoryId.value,
    tag_id: filterTagId.value,
    keyword: filterKeyword.value || undefined,
    sort_by: sortBy.value,
  }
}

const refreshing = ref(false)

function syncQueryFilters() {
  const q = route.query
  filterCategoryId.value = q.category_id ? Number(q.category_id) : undefined
  filterTagId.value = q.tag_id ? Number(q.tag_id) : undefined
}

onMounted(async () => {
  syncQueryFilters()
  await Promise.all([
    catStore.fetchList(),
    tagStore.fetchList(),
  ])
})

watch(
  () => route.query,
  () => {
    syncQueryFilters()
    applyFilter()
  },
)

function handlePeriodChange(range: TimeRange) {
  timeRange.value = range
  applyFilter()
}

async function loadMore() {
  if (!store.hasMore) return
  try {
    await store.fetchList({ ...filterParams(), cursor: store.nextCursor, limit: PAGE_LIMIT }, true)
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

async function onRefresh() {
  refreshing.value = true
  try {
    store.resetList()
    await store.fetchList({ ...filterParams(), limit: INITIAL_LIMIT })
  } catch (e: unknown) {
    showError(getErrorMessage(e, '刷新失败'))
  } finally {
    refreshing.value = false
  }
}

async function applyFilter() {
  store.resetList()
  try {
    await store.fetchList({ ...filterParams(), limit: INITIAL_LIMIT })
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

function clearFilter() {
  filterCategoryId.value = undefined
  filterTagId.value = undefined
  filterKeyword.value = ''
}

function onClearFilter() {
  clearFilter()
  applyFilter()
}

function onToggleSort() {
  sortBy.value = sortBy.value === 'time' ? 'amount' : 'time'
  applyFilter()
}

const catColumns = computed(() => [
  { text: '全部分类', value: -1 },
  ...catStore.list.map((c) => ({ text: c.name, value: c.id })),
])

const tagColumns = computed(() => [
  { text: '全部标签', value: -1 },
  ...tagStore.list.map((t) => ({ text: t.name, value: t.id })),
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
  router.push('/transactions/add')
}

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
  setTimeout(() => {
    isDragging.value = false
  }, 0)
}

function goEdit(id: number) {
  if (isDragging.value) return
  router.push(`/transactions/${id}/edit`)
}

async function handleDelete(id: number) {
  try {
    await showConfirmDialog({
      title: '删除支出',
      message: '确定删除这条支出记录吗？',
    })
  } catch {
    return
  }
  await withMutate(() => store.remove(id), '已删除', '删除失败')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="支出记录" data-testid="transaction-list-nav" />

    <div class="transaction-search-bar">
      <van-search
        v-model="filterKeyword"
        placeholder="搜索金额/分类/标签/备注..."
        shape="round"
        @search="applyFilter"
        @clear="onClearFilter"
      />
    </div>

    <PeriodFilterBar test-id-prefix="transaction-period" @change="handlePeriodChange" />

    <div class="filter-bar">
      <van-tag
        class="filter-bar__item"
        :type="filterCategoryId ? 'primary' : 'default'"
        size="medium"
        @click="showCategoryFilter = true"
      >
        {{ filterCategoryId ? catStore.list.find((c) => c.id === filterCategoryId)?.name : '分类' }}
      </van-tag>
      <van-tag
        class="filter-bar__item"
        :type="filterTagId ? 'primary' : 'default'"
        size="medium"
        @click="showTagFilter = true"
      >
        {{ filterTagId ? tagStore.list.find((t) => t.id === filterTagId)?.name : '标签' }}
      </van-tag>
      <van-tag
        class="filter-bar__item"
        :type="sortBy === 'amount' ? 'primary' : 'default'"
        size="medium"
        @click="onToggleSort"
      >
        {{ sortBy === 'time' ? '时间↓' : '金额↓' }}
      </van-tag>
      <span class="transaction-total-count"> 共 {{ store.total }} 条 </span>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="store.loading"
        :finished="!store.hasMore"
        finished-text="没有更多了"
        :immediate-check="false"
        @load="loadMore"
      >
        <div v-if="store.items.length === 0 && !store.loading" class="empty-placeholder">
          <div class="transaction-empty-icon">📝</div>
          <div class="transaction-empty-text">暂无支出记录</div>
        </div>
        <div
          v-for="transaction in store.items"
          :key="transaction.id"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @click="goEdit(transaction.id)"
        >
          <van-swipe-cell data-testid="transaction-list-swipe-cell">
            <TransactionCard :transaction="transaction" />
            <template #right>
              <van-button
                square
                type="danger"
                text="删除"
                data-testid="transaction-list-delete-btn"
                class="transaction-delete-btn"
                @click.stop="handleDelete(transaction.id)"
              />
            </template>
          </van-swipe-cell>
          <van-divider class="transaction-divider" />
        </div>
      </van-list>
    </van-pull-refresh>

    <div class="transaction-fab">
      <van-button icon="plus" type="primary" round size="large" @click="goAdd" />
    </div>

    <FilterPicker v-model:show="showCategoryFilter" :columns="catColumns" @select="onCatSelect" />

    <FilterPicker v-model:show="showTagFilter" :columns="tagColumns" @select="onTagSelect" />
  </div>
</template>

<style scoped>
.transaction-search-bar {
  padding: var(--space-md) var(--space-lg);
  background: var(--color-surface);
}

.transaction-total-count {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 24px;
  margin-left: auto;
}

.transaction-empty-icon {
  font-size: 48px;
}

.transaction-empty-text {
  margin-top: var(--space-md);
}

.transaction-delete-btn {
  height: 100%;
}

.transaction-divider {
  margin: var(--space-xs) 0;
}

.transaction-fab {
  position: fixed;
  right: var(--space-lg);
  bottom: 70px;
}
</style>
