<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useExpenseStore } from '../stores/expense'
import { useStatisticsStore } from '../stores/statistics'
import { formatAmount } from '../core/format'
import { showError } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import ExpenseCard from '../components/ExpenseCard.vue'

const router = useRouter()
const expenseStore = useExpenseStore()
const statsStore = useStatisticsStore()

const refreshing = ref(false)

async function onRefresh() {
  refreshing.value = true
  try {
    await Promise.all([
      statsStore.fetchOverview(),
      expenseStore.fetchList({ limit: 5 }),
    ])
  } catch (e: unknown) {
showError(getErrorMessage(e, '刷新失败'))
  } finally {
    refreshing.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      statsStore.fetchOverview(),
      expenseStore.fetchList({ limit: 5 }),
    ])
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
})

function goAdd() {
  router.push('/expenses/add')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="个人记账" />

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <!-- 统计卡片 -->
      <van-grid :column-num="2" style="margin: 8px 4px;">
        <van-grid-item>
          <template #default>
            <div class="stat-card" style="margin: 0; width: 100%;">
              <div class="stat-card__amount">{{ formatAmount(statsStore.overview.today) }}</div>
              <div class="stat-card__label">今日支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card" style="margin: 0; width: 100%;">
              <div class="stat-card__amount">{{ formatAmount(statsStore.overview.this_week) }}</div>
              <div class="stat-card__label">本周支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card" style="margin: 0; width: 100%;">
              <div class="stat-card__amount">{{ formatAmount(statsStore.overview.this_month) }}</div>
              <div class="stat-card__label">本月支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card" style="margin: 0; width: 100%;">
              <div class="stat-card__amount">{{ formatAmount(statsStore.overview.this_year) }}</div>
              <div class="stat-card__label">今年支出</div>
            </div>
          </template>
        </van-grid-item>
      </van-grid>

      <!-- 快速记账 -->
      <div style="padding: 12px 16px;">
        <van-button round block type="primary" icon="plus" @click="goAdd">
          记一笔
        </van-button>
      </div>

      <!-- 最近支出 -->
      <div v-if="expenseStore.items.length > 0" style="margin-top: 8px;">
        <van-cell title="最近支出" :value="'共 ' + expenseStore.total + ' 条'" />
        <div v-for="expense in expenseStore.items" :key="expense.id"
             @click="$router.push('/expenses')">
          <ExpenseCard :expense="expense" />
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>
