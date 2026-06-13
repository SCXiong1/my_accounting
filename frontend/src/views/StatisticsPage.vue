<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStatisticsStore } from '../stores/statistics'
import { formatAmount } from '../core/format'
import { showError } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import { useECharts } from '../composables/useECharts'
import { usePeriodFilter } from '../composables/usePeriodFilter'
import ChartPie from '../components/ChartPie.vue'
import ChartBar from '../components/ChartBar.vue'

const router = useRouter()
const store = useStatisticsStore()
const { handleResize } = useECharts()
const {
  activePeriod, periods, timeRange,
  showCustomPopup, pickStep, pickerValue,
  selectPeriod, openCustom, onPickerConfirm, onCancelCustom,
} = usePeriodFilter()

const TAG_PALETTE = ['#E8915A', '#2D6A4F', '#7BA7C9', '#D96B6B', '#C49BD9', '#E8C76B', '#6BC5C5', '#B8927A']

const selectedCategoryId = ref<number | null>(null)
const busy = ref(false)

const catLegendVisible = ref<Record<string, boolean>>({})
const tagLegendVisible = ref<Record<string, boolean>>({})

const filteredCategoryStats = computed(() =>
  store.categoryStats.filter(s => catLegendVisible.value[`${s.category_icon} ${s.category_name}`] !== false)
)

const filteredTagStats = computed(() =>
  store.tagStats.filter(s => tagLegendVisible.value[s.tag_name] !== false)
)

const selectedCatLabel = computed(() => {
  if (!selectedCategoryId.value) return ''
  const cat = store.categoryStats.find(c => c.category_id === selectedCategoryId.value)
  return cat ? `${cat.category_icon} ${cat.category_name}` : ''
})

function clearCatFilter() {
  selectedCategoryId.value = null
}

function goExpenseList() {
  router.push('/expenses')
}

// ── 饼图数据转换 ──────────────────────────────

const catPieData = computed(() =>
  store.categoryStats.map(s => ({
    name: `${s.category_icon} ${s.category_name}`,
    value: s.total_amount,
    itemStyle: { color: s.category_color || undefined },
  }))
)

const tagPieData = computed(() =>
  store.tagStats.map((s, i) => ({
    name: s.tag_name,
    value: s.total_amount,
    itemStyle: { color: TAG_PALETTE[i % TAG_PALETTE.length] },
  }))
)

// ── 柱状图数据提取 ────────────────────────────

const catBarDetails = (m: typeof store.monthlyStats[number]) =>
  m.by_category.map(c => ({ id: c.category_id, name: c.category_name, color: c.category_color, amount: c.amount }))

const tagBarDetails = (m: typeof store.monthlyStats[number]) =>
  m.by_tag.map(t => ({ id: t.tag_id, name: t.tag_name, color: '', amount: t.amount }))

// ── 数据加载 ──────────────────────────────────

async function loadData(fetchAll: boolean) {
  if (busy.value) return
  busy.value = true
  const r = timeRange.value
  const catFilter = selectedCategoryId.value ? String(selectedCategoryId.value) : undefined

  const tasks: Promise<any>[] = []
  if (fetchAll) {
    tasks.push(store.fetchOverview())
    tasks.push(store.fetchByCategory(r.start_time, r.end_time))
    catLegendVisible.value = {}
  }
  tasks.push(store.fetchMonthly(r.start_year, r.start_month, r.end_year, r.end_month, catFilter))
  tasks.push(store.fetchByTag(r.start_time, r.end_time, catFilter))

  try {
    await Promise.all(tasks)
    if (!fetchAll) tagLegendVisible.value = {}
    await nextTick()
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  } finally {
    busy.value = false
  }
}

// ── 响应式监听 ────────────────────────────────

watch(timeRange, () => {
  selectedCategoryId.value = null
  loadData(true)
})
watch(selectedCategoryId, () => loadData(false))

onMounted(() => {
  loadData(true)
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="统计分析" />

    <div class="filter-bar">
      <van-button
        v-for="p in periods" :key="p.key"
        :type="activePeriod === p.key ? 'primary' : 'default'"
        size="small" round
        data-testid="stats-period-btn"
        @click="selectPeriod(p.key)"
      >
        {{ p.label }}
      </van-button>
      <van-button
        :type="activePeriod === 'custom' ? 'primary' : 'default'"
        size="small" round
        @click="openCustom"
      >
        自定义
      </van-button>
    </div>

    <van-grid :column-num="4" :border="false" class="stats-overview-grid">
      <van-grid-item v-for="item in [
        { label: '今日', val: store.overview.today },
        { label: '本周', val: store.overview.this_week },
        { label: '本月', val: store.overview.this_month },
        { label: '今年', val: store.overview.this_year },
      ]" :key="item.label">
        <div class="stat-card stats-overview-card">
          <div class="stat-card__amount stats-overview-amount">{{ formatAmount(item.val) }}</div>
          <div class="stat-card__label">{{ item.label }}</div>
        </div>
      </van-grid-item>
    </van-grid>

    <!-- 分类占比 -->
    <van-cell title="分类占比" title-style="font-weight:500;">
      <template #right-icon>
        <span class="stats-detail-link" @click="goExpenseList">全部明细</span>
      </template>
    </van-cell>
    <div v-if="!busy && store.categoryStats.length === 0" class="empty-placeholder stats-empty">
      <div class="stats-empty-text">暂无数据</div>
    </div>
    <ChartPie v-else :data="catPieData" @legend-change="s => catLegendVisible = s" />

    <div v-if="filteredCategoryStats.length > 0" class="stats-detail-list">
      <div
        v-for="s in filteredCategoryStats.slice(0, 8)" :key="s.category_id"
        class="stats-detail-row"
        data-testid="stats-category-row"
        @click="router.push({ path: '/expenses', query: { category_id: String(s.category_id) } })"
      >
        <span>{{ s.category_icon }}</span>
        <span class="stats-detail-name">{{ s.category_name }}</span>
        <span class="stats-detail-pct">{{ s.percentage }}%</span>
        <span class="stats-detail-amount">{{ formatAmount(s.total_amount) }}</span>
      </div>
    </div>

    <!-- 月度趋势 -->
    <van-cell title="月度趋势" title-style="font-weight:500;">
      <template v-if="selectedCategoryId" #label>
        <van-tag type="primary" closeable @close="clearCatFilter">
          {{ selectedCatLabel }}
        </van-tag>
      </template>
    </van-cell>
    <div v-if="!busy && store.monthlyStats.length === 0" class="empty-placeholder stats-empty">
      <div class="stats-empty-text">暂无数据</div>
    </div>
    <ChartBar v-else :monthly-stats="store.monthlyStats" :get-details="catBarDetails" />

    <!-- 标签占比 -->
    <van-cell title="标签占比" title-style="font-weight:500;" />
    <div v-if="!busy && store.tagStats.length === 0" class="empty-placeholder stats-empty">
      <div class="stats-empty-text">暂无标签数据</div>
    </div>
    <ChartPie v-else :data="tagPieData" data-testid="stats-tag-pie" @legend-change="s => tagLegendVisible = s" />

    <div v-if="filteredTagStats.length > 0" class="stats-detail-list stats-detail-list--bottom">
      <div
        v-for="(t, i) in filteredTagStats.slice(0, 6)" :key="t.tag_id"
        class="stats-detail-row"
        data-testid="stats-tag-row"
        @click="router.push({ path: '/expenses', query: { tag_id: String(t.tag_id) } })"
      >
        <span class="stats-tag-dot" :style="{ background: TAG_PALETTE[i % TAG_PALETTE.length] }" />
        <span class="stats-detail-name">{{ t.tag_name }}</span>
        <span class="stats-detail-pct">{{ t.percentage }}%</span>
        <span class="stats-detail-amount">{{ formatAmount(t.total_amount) }}</span>
      </div>
    </div>

    <!-- 标签月度趋势 -->
    <van-cell title="标签月度趋势" title-style="font-weight:500;" />
    <div v-if="!busy && store.monthlyStats.length === 0" class="empty-placeholder stats-empty">
      <div class="stats-empty-text">暂无数据</div>
    </div>
    <ChartBar v-else :monthly-stats="store.monthlyStats" :get-details="tagBarDetails" :palette="TAG_PALETTE" />
    <div class="stats-bottom-spacer"></div>

    <van-popup v-model:show="showCustomPopup" position="bottom" round>
      <div class="custom-popup">
        <div class="custom-popup__title">
          {{ pickStep === 'start' ? '选择开始月份' : '选择结束月份' }}
        </div>
        <van-date-picker
          :key="pickStep"
          v-model="pickerValue"
          :columns-type="['year', 'month']"
          @confirm="onPickerConfirm"
        />
        <div class="custom-popup__actions">
          <van-button round block @click="onCancelCustom">取消</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.stats-overview-grid {
  margin: var(--space-md) var(--space-sm);
}

.stats-overview-card {
  margin: 0;
  width: 100%;
  padding: var(--space-md) var(--space-sm);
}

.stats-overview-amount {
  font-size: var(--font-size-amount-sm);
}

.stats-detail-link {
  font-size: 13px;
  color: var(--color-accent);
}

.stats-empty {
  padding: var(--space-3xl) 0;
}

.stats-empty-text {
  font-size: 13px;
  color: var(--color-text-placeholder);
}

.stats-detail-list {
  padding: 0 var(--space-lg) var(--space-md);
}

.stats-detail-list--bottom {
  padding-bottom: var(--space-xl);
}

.stats-detail-row {
  display: flex;
  align-items: center;
  padding: var(--space-sm) 0;
  font-size: 13px;
}

.stats-detail-name {
  flex: 1;
  margin-left: var(--space-sm);
  color: var(--color-text-primary);
}

.stats-detail-pct {
  color: var(--color-text-secondary);
  margin-right: var(--space-sm);
}

.stats-detail-amount {
  font-size: 14px;
  font-weight: 600;
}

.stats-tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: var(--space-sm);
  flex-shrink: 0;
}

.stats-bottom-spacer {
  height: var(--space-section);
}

.custom-popup {
  padding: var(--space-lg);
}

.custom-popup__title {
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: var(--space-md);
}

.custom-popup__actions {
  padding: var(--space-sm) var(--space-lg) var(--space-lg);
}
</style>
