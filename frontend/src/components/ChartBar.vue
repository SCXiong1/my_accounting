<script setup lang="ts">
import { onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useECharts, useChart } from '../composables/useECharts'
import type { EChartsFormatterParams } from '../types/echarts'
import type { MonthlyStatItem } from '../stores/statistics'

export interface DetailItem {
  id: number
  name: string
  color: string
  amount: number
}

const props = defineProps<{
  monthlyStats: MonthlyStatItem[]
  getDetails: (m: MonthlyStatItem) => DetailItem[]
  palette?: string[]
}>()

const { init } = useECharts()
let chart: echarts.ECharts | null = null

function render() {
  if (!chartRef.value) return
  if (!chart) {
    chart = init(chartRef.value)
  }
  if (props.monthlyStats.length === 0) {
    chart.clear()
    return
  }

  const detailMap = new Map<number, { name: string; color: string }>()
  for (const m of props.monthlyStats) {
    for (const d of props.getDetails(m)) {
      if (!detailMap.has(d.id)) detailMap.set(d.id, { name: d.name, color: d.color })
    }
  }

  const entries = [...detailMap.entries()]
  const months = props.monthlyStats.map((s) => `${String(s.year).slice(2)}/${s.month}`)
  const series = entries.map(([id, info], i) => ({
    name: info.name,
    type: 'bar' as const,
    stack: 'total',
    barMaxWidth: 40,
    itemStyle: { color: props.palette ? props.palette[i % props.palette.length] : info.color },
    data: props.monthlyStats.map((m) => {
      const d = props.getDetails(m).find((x) => x.id === id)
      return d ? +(d.amount / 100).toFixed(0) : 0
    }),
  }))

  const rows = Math.ceil(detailMap.size / 4)
  const gridBottom = 25 + rows * 20 + 6

  chart.setOption(
    {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: EChartsFormatterParams | EChartsFormatterParams[]) => {
          const list = Array.isArray(params) ? params : [params]
          let html = `<b>${list[0].axisValue ?? ''}</b><br/>`
          let total = 0
          for (const p of list) {
            html += `${p.marker ?? ''} ${p.seriesName ?? ''}: ¥${p.value ?? 0}<br/>`
            total += Number(p.value ?? 0)
          }
          html += `<b>合计: ¥${total}</b>`
          return html
        },
      },
      legend: { orient: 'horizontal', bottom: 5, textStyle: { fontSize: 10 } },
      grid: { left: 10, right: 10, top: 20, bottom: gridBottom },
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
    },
    { notMerge: true },
  )
}

const { chartRef } = useChart({
  render,
  watchSource: () => props.monthlyStats,
})

onUnmounted(() => {
  chart = null
})
</script>

<template>
  <div ref="chartRef" class="chart-box chart-bar" data-testid="chart-bar" />
</template>

<style scoped>
.chart-bar {
  height: 320px;
}
</style>
