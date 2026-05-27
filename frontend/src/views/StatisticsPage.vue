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

const TAG_PALETTE = ['#1989fa', '#07c160', '#ff976a', '#ee0a24', '#9c27b0', '#ffc300', '#00bcd4', '#795548']

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

    <van-grid :column-num="4" :border="false" style="margin: 8px 4px;">
      <van-grid-item v-for="item in [
        { label: '今日', val: store.overview.today },
        { label: '本周', val: store.overview.this_week },
        { label: '本月', val: store.overview.this_month },
        { label: '今年', val: store.overview.this_year },
      ]" :key="item.label">
        <div class="stat-card" style="margin:0;width:100%;padding:10px 4px;">
          <div class="stat-card__amount" style="font-size:15px;">{{ formatAmount(item.val) }}</div>
          <div class="stat-card__label">{{ item.label }}</div>
        </div>
      </van-grid-item>
    </van-grid>

    <!-- 分类占比 -->
    <van-cell title="分类占比" title-style="font-weight:500;">
      <template #right-icon>
        <span style="font-size:13px;color:#1989fa;" @click="goExpenseList">全部明细</span>
      </template>
    </van-cell>
    <div v-if="!busy && store.categoryStats.length === 0" class="empty-placeholder" style="padding:30px 0;">
      <div style="font-size:13px;color:#c8c9cc;">暂无数据</div>
    </div>
    <ChartPie v-else :data="catPieData" @legend-change="s => catLegendVisible = s" />

    <div v-if="filteredCategoryStats.length > 0" style="padding:0 16px 12px;">
      <div
        v-for="s in filteredCategoryStats.slice(0, 8)" :key="s.category_id"
        style="display:flex;align-items:center;padding:4px 0;font-size:13px;"
        @click="router.push({ path: '/expenses', query: { category_id: String(s.category_id) } })"
      >
        <span>{{ s.category_icon }}</span>
        <span style="flex:1;margin-left:6px;color:#323233;">{{ s.category_name }}</span>
        <span style="color:#969799;margin-right:8px;">{{ s.percentage }}%</span>
        <span style="font-weight:500;">{{ formatAmount(s.total_amount) }}</span>
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
    <div v-if="!busy && store.monthlyStats.length === 0" class="empty-placeholder" style="padding:30px 0;">
      <div style="font-size:13px;color:#c8c9cc;">暂无数据</div>
    </div>
    <ChartBar v-else :monthly-stats="store.monthlyStats" :get-details="catBarDetails" />

    <!-- 标签占比 -->
    <van-cell title="标签占比" title-style="font-weight:500;" />
    <div v-if="!busy && store.tagStats.length === 0" class="empty-placeholder" style="padding:30px 0;">
      <div style="font-size:13px;color:#c8c9cc;">暂无标签数据</div>
    </div>
    <ChartPie v-else :data="tagPieData" @legend-change="s => tagLegendVisible = s" />

    <div v-if="filteredTagStats.length > 0" style="padding:0 16px 20px;">
      <div
        v-for="(t, i) in filteredTagStats.slice(0, 6)" :key="t.tag_id"
        style="display:flex;align-items:center;padding:4px 0;font-size:13px;"
        @click="router.push({ path: '/expenses', query: { tag_id: String(t.tag_id) } })"
      >
        <span style="width:8px;height:8px;border-radius:50%;margin-right:6px;flex-shrink:0;"
          :style="{ background: TAG_PALETTE[i % TAG_PALETTE.length] }" />
        <span style="flex:1;color:#323233;">{{ t.tag_name }}</span>
        <span style="color:#969799;margin-right:8px;">{{ t.percentage }}%</span>
        <span style="font-weight:500;">{{ formatAmount(t.total_amount) }}</span>
      </div>
    </div>

    <!-- 标签月度趋势 -->
    <van-cell title="标签月度趋势" title-style="font-weight:500;" />
    <div v-if="!busy && store.monthlyStats.length === 0" class="empty-placeholder" style="padding:30px 0;">
      <div style="font-size:13px;color:#c8c9cc;">暂无数据</div>
    </div>
    <ChartBar v-else :monthly-stats="store.monthlyStats" :get-details="tagBarDetails" :palette="TAG_PALETTE" />
    <div style="height:20px;"></div>

    <van-popup v-model:show="showCustomPopup" position="bottom" round>
      <div style="padding:16px;">
        <div style="text-align:center;font-size:16px;font-weight:500;margin-bottom:12px;">
          {{ pickStep === 'start' ? '选择开始月份' : '选择结束月份' }}
        </div>
        <van-date-picker
          :key="pickStep"
          v-model="pickerValue"
          :columns-type="['year', 'month']"
          @confirm="onPickerConfirm"
        />
        <div style="padding:8px 16px 16px;">
          <van-button round block @click="onCancelCustom">取消</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>
