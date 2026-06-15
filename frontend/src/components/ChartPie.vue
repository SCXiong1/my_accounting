<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { centsToYuan } from '../core/format'
import { useECharts } from '../composables/useECharts'

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

const { init, handleResize } = useECharts()
const chartRef = ref<HTMLDivElement>()
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
      data: props.data,
    }],
  }, { notMerge: true })
}

watch(() => props.data, render, { deep: true })

onMounted(async () => {
  await nextTick()
  render()
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart = null
})
</script>

<template>
  <div ref="chartRef" class="chart-box chart-pie" data-testid="chart-pie"></div>
</template>

<style scoped>
.chart-pie {
  height: 280px;
}
</style>
