<script setup lang="ts">
import { onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { centsToYuan } from '../core/format'
import { useECharts, useChart } from '../composables/useECharts'
import type { EChartsFormatterParams } from '../types/echarts'

export interface PieItem {
  name: string
  value: number
  itemStyle: { color?: string }
}

const props = defineProps<{
  data: PieItem[]
}>()

const emit = defineEmits<{
  'legend-change': [selected: Record<string, boolean>]
}>()

const { init } = useECharts()
let chart: echarts.ECharts | null = null

function render() {
  if (!chartRef.value) return
  if (!chart) {
    chart = init(chartRef.value, (sel) => emit('legend-change', { ...sel }))
  }
  if (props.data.length === 0) {
    chart.setOption({ series: [{ type: 'pie', data: [] }] }, { notMerge: true })
    return
  }
  chart.setOption(
    {
      tooltip: {
        trigger: 'item',
        formatter: (p: EChartsFormatterParams) =>
          `${p.name}<br/>金额: ¥${centsToYuan(p.value as number)}<br/>占比: ${p.percent ?? 0}%`,
      },
      legend: { orient: 'horizontal', bottom: 0, textStyle: { fontSize: 11 } },
      series: [
        {
          type: 'pie',
          radius: ['40%', '65%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: false,
          selectedMode: false,
          itemStyle: { borderRadius: 2, borderColor: '#fff', borderWidth: 1 },
          label: { fontSize: 10 },
          data: props.data,
        },
      ],
    },
    { notMerge: true },
  )
}

const { chartRef } = useChart({
  render,
  watchSource: () => props.data,
})

onUnmounted(() => {
  chart = null
})
</script>

<template>
  <div ref="chartRef" class="chart-box chart-pie" data-testid="chart-pie" />
</template>

<style scoped>
.chart-pie {
  height: 280px;
}
</style>
