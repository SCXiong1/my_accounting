import * as echarts from 'echarts'
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

interface LegendSelectChangedEvent {
  selected: Record<string, boolean>
}

export function useECharts() {
  const charts: echarts.ECharts[] = []

  function init(
    el: HTMLDivElement,
    onLegendChange?: (selected: Record<string, boolean>) => void,
  ): echarts.ECharts {
    const chart = echarts.init(el)
    if (onLegendChange) {
      chart.on('legendselectchanged', (params) => {
        const event = params as LegendSelectChangedEvent
        onLegendChange(event.selected)
      })
    }
    charts.push(chart)
    return chart
  }

  function handleResize() {
    for (const c of charts) c.resize()
  }

  onUnmounted(() => {
    for (const c of charts) c.dispose()
    charts.length = 0
  })

  return { init, handleResize }
}

export function useChart(config: { render: () => void; watchSource: () => unknown }) {
  const chartRef = ref<HTMLDivElement>()

  watch(config.watchSource, () => config.render(), { deep: true })

  onMounted(async () => {
    await nextTick()
    config.render()
    window.addEventListener('resize', config.render)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', config.render)
  })

  return { chartRef }
}
