<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useECharts } from '../composables/useECharts'

export interface DetailItem {
  id: number
  name: string
  color: string
  amount: number
}

const props = defineProps<{
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  monthlyStats: any[]
  getDetails: (m: any) => DetailItem[]
  palette?: string[]
}>()

const { init, handleResize } = useECharts()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chartRef.value) return
  if (!chart) {
    chart = init(chartRef.value)
  }
  if (props.monthlyStats.length === 0) {
    chart.setOption({ series: [{ type: 'bar', data: [] }] }, { notMerge: true })
    return
  }

  const detailMap = new Map<number, { name: string; color: string }>()
  for (const m of props.monthlyStats) {
    for (const d of props.getDetails(m)) {
      if (!detailMap.has(d.id)) detailMap.set(d.id, { name: d.name, color: d.color })
    }
  }

  const entries = [...detailMap.entries()]
  const months = props.monthlyStats.map(s => `${String(s.year).slice(2)}/${s.month}`)
  const series = entries.map(([id, info], i) => ({
    name: info.name,
    type: 'bar' as const,
    stack: 'total',
    barMaxWidth: 40,
    itemStyle: { color: props.palette ? props.palette[i % props.palette.length] : info.color },
    data: props.monthlyStats.map(m => {
      const d = props.getDetails(m).find(x => x.id === id)
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
}

watch(() => props.monthlyStats, render, { deep: true })

onMounted(() => {
  render()
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div ref="chartRef" class="chart-box" data-testid="chart-bar" style="height:320px;"></div>
</template>
