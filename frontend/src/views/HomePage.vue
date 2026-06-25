<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore } from '../stores/transaction'
import { useStatisticsStore } from '../stores/statistics'
import { formatAmount } from '../core/format'
import { showError } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import TransactionCard from '../components/TransactionCard.vue'

const router = useRouter()
const transactionStore = useTransactionStore()
const statsStore = useStatisticsStore()

const refreshing = ref(false)

async function onRefresh() {
  refreshing.value = true
  try {
    await Promise.all([statsStore.fetchOverview(), transactionStore.fetchList({ limit: 5 })])
  } catch (e: unknown) {
    showError(getErrorMessage(e, '刷新失败'))
  } finally {
    refreshing.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.all([statsStore.fetchOverview(), transactionStore.fetchList({ limit: 5 })])
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  }
})

function goAdd() {
  router.push('/transactions/add')
}
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="个人记账" />

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-grid :column-num="2" class="home-grid">
        <van-grid-item>
          <template #default>
            <div class="stat-card home-stat-card" data-testid="home-stat-today">
              <div class="stat-card__amount">
                {{ formatAmount(statsStore.overview.today) }}
              </div>
              <div class="stat-card__label">今日支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card home-stat-card" data-testid="home-stat-week">
              <div class="stat-card__amount">
                {{ formatAmount(statsStore.overview.this_week) }}
              </div>
              <div class="stat-card__label">本周支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card home-stat-card" data-testid="home-stat-month">
              <div class="stat-card__amount">
                {{ formatAmount(statsStore.overview.this_month) }}
              </div>
              <div class="stat-card__label">本月支出</div>
            </div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #default>
            <div class="stat-card home-stat-card" data-testid="home-stat-year">
              <div class="stat-card__amount">
                {{ formatAmount(statsStore.overview.this_year) }}
              </div>
              <div class="stat-card__label">今年支出</div>
            </div>
          </template>
        </van-grid-item>
      </van-grid>

      <div class="home-add-btn">
        <van-button
          round
          block
          type="primary"
          icon="plus"
          class="van-button--accent"
          @click="goAdd"
        >
          记一笔
        </van-button>
      </div>

      <div v-if="transactionStore.items.length > 0" class="home-recent">
        <van-cell title="最近支出" :value="'共 ' + transactionStore.total + ' 条'" />
        <div
          v-for="transaction in transactionStore.items"
          :key="transaction.id"
          @click="$router.push('/transactions')"
        >
          <TransactionCard :transaction="transaction" />
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.home-grid {
  margin: var(--space-md) var(--space-sm);
}

.home-stat-card {
  margin: 0;
  width: 100%;
}

.home-add-btn {
  padding: var(--space-lg) var(--space-lg);
}

.home-recent {
  margin-top: var(--space-section);
}
</style>
