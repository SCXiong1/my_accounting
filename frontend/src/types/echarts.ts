import type { CallbackDataParams } from 'echarts/types/dist/shared'

/** ECharts tooltip formatter params with common fields typed */
export type EChartsFormatterParams = CallbackDataParams & {
  seriesName?: string
  name?: string
  value?: number | string
  percent?: number
  dataIndex?: number
  marker?: string
  axisValue?: string
}
