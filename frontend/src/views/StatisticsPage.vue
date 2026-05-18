<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import api from '../lib/api'
import { useStatisticsStore } from '../stores/statistics'
import { formatAmount, centsToYuan } from '../core/format'
import { showError } from '../lib/feedback'
import { getErrorMessage } from '../lib/error'

const router = useRouter()
const store = useStatisticsStore()

type Period = 'month' | '3month' | '6month' | 'year' | 'custom'
const activePeriod = ref<Period>('month')
const selectedCategoryId = ref<number | null>(null)
const busy = ref(false)

const showCustomPopup = ref(false)
const pickStep = ref<'start' | 'end'>('start')
const customStartDate = ref(new Date())
const customEndDate = ref(new Date())
const pickerValue = ref<any[]>([new Date().getFullYear(), new Date().getMonth() + 1])
const pendingStart = ref<Date | null>(null)

const overview = ref({ today: 0, this_week: 0, this_month: 0, this_year: 0 })

const pieRef = ref<HTMLDivElement>()
const barRef = ref<HTMLDivElement>()
const tagPieRef = ref<HTMLDivElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let tagPieChart: echarts.ECharts | null = null

const TAG_PALETTE = ['#1989fa', '#07c160', '#ff976a', '#ee0a24', '#9c27b0', '#ffc300', '#00bcd4', '#795548']

const periods: { key: Period; label: string }[] = [
  { key: 'month', label: '本月' },
  { key: '3month', label: '近3月' },
  { key: '6month', label: '近6月' },
  { key: 'year', label: '今年' },
]

const timeRange = computed(() => {
  const now = new Date()
  let start: Date
  let end = now

  switch (activePeriod.value) {
    case 'month':
      start = new Date(now.getFullYear(), now.getMonth(), 1)
      break
    case '3month':
      start = new Date(now.getFullYear(), now.getMonth() - 2, 1)
      break
    case '6month':
      start = new Date(now.getFullYear(), now.getMonth() - 5, 1)
      break
    case 'year':
      start = new Date(now.getFullYear(), 0, 1)
      break
    case 'custom':
      start = customStartDate.value
      end = new Date(customEndDate.value)
      end.setMonth(end.getMonth() + 1, 0)  // 该月最后一天
      end.setHours(23, 59, 59)
      break
  }

  return {
    start_time: Math.floor(start.getTime() / 1000),
    end_time: Math.floor(end.getTime() / 1000),
    start_year: start.getFullYear(),
    start_month: start.getMonth() + 1,
    end_year: end.getFullYear(),
    end_month: end.getMonth() + 1,
  }
})

const selectedCatLabel = computed(() => {
  if (!selectedCategoryId.value) return ''
  const cat = store.categoryStats.find(c => c.category_id === selectedCategoryId.value)
  return cat ? `${cat.category_icon} ${cat.category_name}` : ''
})

function selectPeriod(p: Period) {
  if (activePeriod.value === p) return
  activePeriod.value = p
  selectedCategoryId.value = null
}

function openCustom() {
  pendingStart.value = null
  pickStep.value = 'start'
  pickerValue.value = [customStartDate.value.getFullYear(), customStartDate.value.getMonth() + 1]
  showCustomPopup.value = true
}

function onPickerConfirm({ selectedValues }: { selectedValues: number[] }) {
  if (pickStep.value === 'start') {
    pendingStart.value = new Date(selectedValues[0], selectedValues[1] - 1, 1)
    pickStep.value = 'end'
    pickerValue.value = [customEndDate.value.getFullYear(), customEndDate.value.getMonth() + 1]
  } else {
    const endDate = new Date(selectedValues[0], selectedValues[1] - 1, 1)
    const startDate = pendingStart.value!
    customStartDate.value = startDate
    customEndDate.value = endDate < startDate ? new Date(startDate) : endDate
    showCustomPopup.value = false
    selectedCategoryId.value = null
    activePeriod.value = 'custom'
  }
}

function onCancelCustom() {
  showCustomPopup.value = false
}

function onCatPieClick(params: any) {
  const cid = params.data?.categoryId
  if (cid) {
    router.push({ path: '/expenses', query: { category_id: String(cid) } })
  }
}

function onTagPieClick(params: any) {
  const tid = params.data?.tagId
  if (tid) {
    router.push({ path: '/expenses', query: { tag_id: String(tid) } })
  }
}

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
    await nextTick()
    renderPieChart()
    renderBarChart()
    renderTagPieChart()
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
    await nextTick()
    renderBarChart()
    renderTagPieChart()
  } catch (e: unknown) {
    showError(getErrorMessage(e, '加载失败'))
  } finally {
    busy.value = false
  }
}

// === 分类饼图 ===
function renderPieChart() {
  if (!pieRef.value) return
  if (!pieChart) {
    pieChart = echarts.init(pieRef.value)
    pieChart.on('click', onCatPieClick)
  }

  if (store.categoryStats.length === 0) {
    pieChart.setOption({ series: [{ type: 'pie', data: [] }] }, { notMerge: true })
    return
  }

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p: any) =>
        `${p.name}<br/>金额: ¥${centsToYuan(p.value)}<br/>占比: ${p.percent}%`,
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: { fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: false,
      selectedMode: false,
      itemStyle: { borderRadius: 2, borderColor: '#fff', borderWidth: 1 },
      label: { fontSize: 10 },
      data: store.categoryStats.map(s => ({
        name: `${s.category_icon} ${s.category_name}`,
        value: s.total_amount,
        categoryId: s.category_id,
        itemStyle: { color: s.category_color || undefined },
      })),
    }],
  }, { notMerge: true })
}

// === 月度堆叠柱状图 ===
function renderBarChart() {
  if (!barRef.value) return
  if (!barChart) {
    barChart = echarts.init(barRef.value)
  }

  if (store.monthlyStats.length === 0) {
    barChart.setOption({ series: [{ type: 'bar', data: [] }] }, { notMerge: true })
    return
  }

  // 收集所有出现的分类（去重）
  const catMap = new Map<number, { name: string; color: string }>()
  for (const m of store.monthlyStats) {
    for (const c of m.by_category) {
      if (!catMap.has(c.category_id)) {
        catMap.set(c.category_id, { name: c.category_name, color: c.category_color })
      }
    }
  }

  const months = store.monthlyStats.map(s => `${s.month}月`)
  const series = [...catMap.entries()].map(([cid, info]) => ({
    name: info.name,
    type: 'bar' as const,
    stack: 'total',
    barMaxWidth: 40,
    itemStyle: { color: info.color },
    data: store.monthlyStats.map(m => {
      const detail = m.by_category.find(c => c.category_id === cid)
      return detail ? +(detail.amount / 100).toFixed(0) : 0
    }),
  }))

  barChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        let html = `<b>${params[0].axisValue}</b><br/>`
        let total = 0
        for (const p of params) {
          html += `${p.marker} ${p.seriesName}: ¥${p.value}<br/>`
          total += Number(p.value)
        }
        html += `<b>合计: ¥${total}</b>`
        return html
      },
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: { fontSize: 10 },
    },
    grid: { left: 10, right: 10, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { rotate: months.length > 6 ? 30 : 0, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (v: number) => `¥${v}` },
      splitLine: { lineStyle: { type: 'dashed' } },
    },
    series,
  }, { notMerge: true })
}

// === 标签饼图 ===
function renderTagPieChart() {
  if (!tagPieRef.value) return
  if (!tagPieChart) {
    tagPieChart = echarts.init(tagPieRef.value)
    tagPieChart.on('click', onTagPieClick)
  }

  if (store.tagStats.length === 0) {
    tagPieChart.setOption({ series: [{ type: 'pie', data: [] }] }, { notMerge: true })
    return
  }

  tagPieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p: any) =>
        `${p.name}<br/>金额: ¥${centsToYuan(p.value)}<br/>占比: ${p.percent}%`,
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: { fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: false,
      selectedMode: false,
      itemStyle: { borderRadius: 2, borderColor: '#fff', borderWidth: 1 },
      label: { fontSize: 10 },
      data: store.tagStats.map((s, i) => ({
        name: s.tag_name,
        value: s.total_amount,
        tagId: s.tag_id,
        itemStyle: { color: TAG_PALETTE[i % TAG_PALETTE.length] },
      })),
    }],
  }, { notMerge: true })
}

function handleResize() {
  pieChart?.resize()
  barChart?.resize()
  tagPieChart?.resize()
}

watch(timeRange, loadAll)
watch(selectedCategoryId, loadFiltered)

onMounted(() => {
  loadAll()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  barChart?.dispose()
  tagPieChart?.dispose()
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
      <van-grid-item>
        <div class="stat-card" style="margin:0;width:100%;padding:10px 4px;">
          <div class="stat-card__amount" style="font-size:15px;">{{ formatAmount(overview.today) }}</div>
          <div class="stat-card__label">今日</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat-card" style="margin:0;width:100%;padding:10px 4px;">
          <div class="stat-card__amount" style="font-size:15px;">{{ formatAmount(overview.this_week) }}</div>
          <div class="stat-card__label">本周</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat-card" style="margin:0;width:100%;padding:10px 4px;">
          <div class="stat-card__amount" style="font-size:15px;">{{ formatAmount(overview.this_month) }}</div>
          <div class="stat-card__label">本月</div>
        </div>
      </van-grid-item>
      <van-grid-item>
        <div class="stat-card" style="margin:0;width:100%;padding:10px 4px;">
          <div class="stat-card__amount" style="font-size:15px;">{{ formatAmount(overview.this_year) }}</div>
          <div class="stat-card__label">今年</div>
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

    <div v-if="store.categoryStats.length > 0" style="padding:0 16px 12px;">
      <div
        v-for="s in store.categoryStats.slice(0, 8)" :key="s.category_id"
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

    <div v-if="store.tagStats.length > 0" style="padding:0 16px 20px;">
      <div
        v-for="(t, i) in store.tagStats.slice(0, 6)" :key="t.tag_id"
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
