<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showConfirmDialog } from 'vant'
import { getErrorMessage } from '../lib/error'
import { showSuccess, showError } from '../lib/feedback'
import { useExpenseStore } from '../stores/expense'
import { useCategoryStore } from '../stores/category'
import { useTagStore } from '../stores/tag'
import ExpenseCard from '../components/ExpenseCard.vue'

const router = useRouter()
const route = useRoute()
const store = useExpenseStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

// 筛选条件
const filterCategoryId = ref<number | null>(null)
const filterTagId = ref<number | null>(null)
const filterKeyword = ref('')
const sortBy = ref('time')

const showCategoryFilter = ref(false)
const showTagFilter = ref(false)

const limit = 20

// 下拉刷新
const refreshing = ref(false)

onMounted(async () => {
  const q = route.query
  if (q.category_id) filterCategoryId.value = Number(q.category_id)
  if (q.tag_id) filterTagId.value = Number(q.tag_id)
  await Promise.all([
    store.fetchList({
      limit,
      sort_by: 'time',
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
    }),
    catStore.fetchList(),
    tagStore.fetchList(),
  ])
})

async function loadMore() {
  if (!store.hasMore || store.loading) return
  try {
    await store.fetchList({
      cursor: store.nextCursor,
      limit,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || null,
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
      limit,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || null,
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
      limit,
      category_id: filterCategoryId.value,
      tag_id: filterTagId.value,
      keyword: filterKeyword.value || null,
      sort_by: sortBy.value,
    })
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
}

function clearFilter() {
  filterCategoryId.value = null
  filterTagId.value = null
  filterKeyword.value = ''
}

function goAdd() {
  router.push('/expenses/add')
}

function goEdit(id: number) {
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
  try {
    await store.remove(id)
showSuccess('已删除')
  } catch (e: unknown) {
showError(getErrorMessage(e, '删除失败'))
  }
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="支出记录" />

    <!-- 搜索栏 -->
    <div style="padding: 8px 12px; background: #fff;">
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
      <span style="font-size: 12px; color: #969799; line-height: 24px; margin-left: auto;">
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
          <div style="font-size: 48px;">📝</div>
          <div style="margin-top: 12px;">暂无支出记录</div>
        </div>
        <div v-for="expense in store.items" :key="expense.id" @click="goEdit(expense.id)">
          <van-swipe-cell>
            <ExpenseCard :expense="expense" />
            <template #right>
              <van-button
                square
                type="danger"
                text="删除"
@click.stop="handleDelete(expense.id)"
                style="height: 100%;"
              />
            </template>
          </van-swipe-cell>
          <van-divider style="margin: 0;" />
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 新增按钮 -->
    <div style="position: fixed; right: 16px; bottom: 70px;">
      <van-button
        icon="plus"
        type="primary"
        round
        size="large"
        @click="goAdd"
      />
    </div>

    <!-- 分类筛选 -->
    <van-popup v-model:show="showCategoryFilter" position="bottom" round>
      <van-picker
        :columns="[{ text: '全部分类', value: -1 }, ...catStore.list.map(c => ({ text: c.name, value: c.id }))]"
        :default-index="0"
        @confirm="({ selectedValues }: { selectedValues: number[] }) => { filterCategoryId = selectedValues[0] === -1 ? null : selectedValues[0]; showCategoryFilter = false; applyFilter() }"
        @cancel="showCategoryFilter = false"
      />
    </van-popup>

    <!-- 标签筛选 -->
    <van-popup v-model:show="showTagFilter" position="bottom" round>
      <van-picker
        :columns="[{ text: '全部标签', value: -1 }, ...tagStore.list.map(t => ({ text: t.name, value: t.id }))]"
        :default-index="0"
        @confirm="({ selectedValues }: { selectedValues: number[] }) => { filterTagId = selectedValues[0] === -1 ? null : selectedValues[0]; showTagFilter = false; applyFilter() }"
        @cancel="showTagFilter = false"
      />
    </van-popup>
  </div>
</template>
