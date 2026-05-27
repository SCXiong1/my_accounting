<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import api from '../lib/api'
import { useStatisticsStore } from '../stores/statistics'
import { formatAmount, centsToYuan } from '../core/format'
import { showError } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'
import { useECharts } from '../composables/useECharts'
import { usePeriodFilter } from '../composables/usePeriodFilter'

const router = useRouter()
const store = useStatisticsStore()
const { init, handleResize } = useECharts()
const {
  activePeriod, periods, timeRange,
  showCustomPopup, pickStep, pickerValue,
  selectPeriod, openCustom, onPickerConfirm, onCancelCustom,
} = usePeriodFilter()

const TAG_PALETTE = ['#1989fa', '#07c160', '#ff976a', '#ee0a24', '#9c27b0', '#ffc300', '#00bcd4', '#795548']

const selectedCategoryId = ref<number | null>(null)
const busy = ref(false)
const overview = ref({ today: 0, this_week: 0, this_month: 0, this_year: 0 })

const pieRef = ref<HTMLDivElement>()
const barRef = ref<HTMLDivElement>()
const tagPieRef = ref<HTMLDivElement>()
const tagBarRef = ref<HTMLDivElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let tagPieChart: echarts.ECharts | null = null
let tagBarChart: echarts.ECharts | null = null

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

async function fetchOverview() {
  const res = await api.get('/v1/statistics/overview')
  overview.value = res.data
}

// ── 通用渲染函数 ──────────────────────────────

interface PieItem {
  name: string
  value: number
  itemStyle: { color?: string }
}

function renderPieChart(
  chartRef: HTMLDivElement | undefined,
  chart: echarts.ECharts | null,
  data: PieItem[],
  legendVisible: ReturnType<typeof ref<Record<string, boolean>>>,
): echarts.ECharts | null {
  if (!chartRef) return null
  if (!chart) {
    chart = init(chartRef, (sel) => { legendVisible.value = { ...sel } })
  }
  if (data.length === 0) {
    chart.setOption({ series: [{ type: 'pie', data: [] }] }, { notMerge: true })
    return chart
  }
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => `${p.name}<br/>金额: ¥${centsToYuan(p.value)}<br/>占比: ${p.percent}%`,
    },
    legend: { orient: 'horizontal', bottom: 0, textStyle: { fontSize: 11 } },
    series: [{
      type: 'pie', radius: ['40%', '65%'], center: ['50%', '42%'],
      avoidLabelOverlap: false, selectedMode: false,
      itemStyle: { borderRadius: 2, borderColor: '#fff', borderWidth: 1 },
      label: { fontSize: 10 },
      data,
    }],
  }, { notMerge: true })
  return chart
}

function renderBarChart(
  chartRef: HTMLDivElement | undefined,
  chart: echarts.ECharts | null,
  monthlyStats: typeof store.monthlyStats,
  getDetails: (m: typeof store.monthlyStats[number]) => { id: number; name: string; color: string; amount: number }[],
  palette?: string[],
): echarts.ECharts | null {
  if (!chartRef) return null
  if (!chart) {
    chart = init(chartRef)
  }
  if (monthlyStats.length === 0) {
    chart.setOption({ series: [{ type: 'bar', data: [] }] }, { notMerge: true })
    return chart
  }

  const detailMap = new Map<number, { name: string; color: string }>()
  for (const m of monthlyStats) {
    for (const d of getDetails(m)) {
      if (!detailMap.has(d.id)) detailMap.set(d.id, { name: d.name, color: d.color })
    }
  }

  const entries = [...detailMap.entries()]
  const months = monthlyStats.map(s => `${String(s.year).slice(2)}/${s.month}`)
  const series = entries.map(([id, info], i) => ({
    name: info.name,
    type: 'bar' as const,
    stack: 'total',
    barMaxWidth: 40,
    itemStyle: { color: palette ? palette[i % palette.length] : info.color },
    data: monthlyStats.map(m => {
      const d = getDetails(m).find(x => x.id === id)
      return d ? +(d.amount / 100).toFixed(0) : 0
    }),
  }))

  const rows = Math.ceil(detailMap.size / 4)
  const gridBottom = 25 + rows * 20 + 6

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        let html = `<b>${params[0].axisValue}</b><br/>`
        let total = 0
        for (const p of params) { html += `${p.marker} ${p.seriesName}: ¥${p.value}<br/>`; total += Number(p.value) }
        html += `<b>合计: ¥${total}</b>`
        return html
      },
    },
    legend: { orient: 'horizontal', bottom: 5, textStyle: { fontSize: 10 } },
    grid: { left: 10, right: 10, top: 20, bottom: gridBottom },
    xAxis: {
      type: 'category', data: months,
      axisLabel: { rotate: months.length > 6 ? 30 : 0, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v: number) => `¥${v}` },
      splitLine: { lineStyle: { type: 'dashed' } },
    },
    series,
  }, { notMerge: true })
  return chart
}

// ── 数据加载 ──────────────────────────────────

async function loadAll() {
  if (busy.value) return
  busy.value = true
  const r = timeRange.value
  const catFilter = selectedCategoryId.value ? String(selectedCategoryId.value) : undefined

  try {
    await Promise.all([
      fetchOverview(),
      store.fetchByCategory(r.start_time, r.end_time),
      store.fetchMonthly(r.start_year, r.start_month, r.end_year, r.end_month, catFilter),
      store.fetchByTag(r.start_time, r.end_time, catFilter),
    ])
    catLegendVisible.value = {}
    tagLegendVisible.value = {}
    await nextTick()
    pieChart = renderPieChart(pieRef.value, pieChart,
      store.categoryStats.map(s => ({
        name: `${s.category_icon} ${s.category_name}`,
        value: s.total_amount,
        itemStyle: { color: s.category_color || undefined },
      })), catLegendVisible)
    barChart = renderBarChart(barRef.value, barChart, store.monthlyStats,
      m => m.by_category.map(c => ({ id: c.category_id, name: c.category_name, color: c.category_color, amount: c.amount })))
    tagPieChart = renderPieChart(tagPieRef.value, tagPieChart,
      store.tagStats.map((s, i) => ({
        name: s.tag_name,
        value: s.total_amount,
        itemStyle: { color: TAG_PALETTE[i % TAG_PALETTE.length] },
      })), tagLegendVisible)
    tagBarChart = renderBarChart(tagBarRef.value, tagBarChart, store.monthlyStats,
      m => m.by_tag.map(t => ({ id: t.tag_id, name: t.tag_name, color: '', amount: t.amount })), TAG_PALETTE)
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  } finally {
    busy.value = false
  }
}

async function loadFiltered() {
  if (busy.value) return
  busy.value = true
  const r = timeRange.value
  const catFilter = selectedCategoryId.value ? String(selectedCategoryId.value) : undefined

  try {
    await Promise.all([
      store.fetchMonthly(r.start_year, r.start_month, r.end_year, r.end_month, catFilter),
      store.fetchByTag(r.start_time, r.end_time, catFilter),
    ])
    tagLegendVisible.value = {}
    await nextTick()
    barChart = renderBarChart(barRef.value, barChart, store.monthlyStats,
      m => m.by_category.map(c => ({ id: c.category_id, name: c.category_name, color: c.category_color, amount: c.amount })))
    tagPieChart = renderPieChart(tagPieRef.value, tagPieChart,
      store.tagStats.map((s, i) => ({
        name: s.tag_name,
        value: s.total_amount,
        itemStyle: { color: TAG_PALETTE[i % TAG_PALETTE.length] },
      })), tagLegendVisible)
    tagBarChart = renderBarChart(tagBarRef.value, tagBarChart, store.monthlyStats,
      m => m.by_tag.map(t => ({ id: t.tag_id, name: t.tag_name, color: '', amount: t.amount })), TAG_PALETTE)
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  } finally {
    busy.value = false
  }
}

// ── 响应式监听 ────────────────────────────────

watch(timeRange, () => {
  selectedCategoryId.value = null
  loadAll()
})
watch(selectedCategoryId, loadFiltered)

// 初始加载 + resize
onMounted(() => {
  loadAll()
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
        { label: '今日', val: overview.today },
        { label: '本周', val: overview.this_week },
        { label: '本月', val: overview.this_month },
        { label: '今年', val: overview.this_year },
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
    <div v-else ref="pieRef" class="chart-box" style="height:280px;"></div>

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
    <div v-else ref="barRef" class="chart-box" style="height:320px;"></div>

    <!-- 标签占比 -->
    <van-cell title="标签占比" title-style="font-weight:500;" />
    <div v-if="!busy && store.tagStats.length === 0" class="empty-placeholder" style="padding:30px 0;">
      <div style="font-size:13px;color:#c8c9cc;">暂无标签数据</div>
    </div>
    <div v-else ref="tagPieRef" class="chart-box" style="height:280px;"></div>

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
    <div v-else ref="tagBarRef" class="chart-box" style="height:320px;"></div>
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
