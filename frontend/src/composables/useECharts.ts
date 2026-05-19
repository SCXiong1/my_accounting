import * as echarts from 'echarts'
import { onUnmounted } from 'vue'

export function useECharts() {
  const charts: echarts.ECharts[] = []

  function init(el: HTMLDivElement, onLegendChange?: (selected: Record<string, boolean>) => void): echarts.ECharts {
    const chart = echarts.init(el)
    if (onLegendChange) {
      chart.on('legendselectchanged', (params: any) => onLegendChange(params.selected))
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
