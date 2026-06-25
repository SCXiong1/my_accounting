import { describe, it, expect } from 'vitest'
import { usePeriodFilter } from '../usePeriodFilter'

describe('usePeriodFilter', () => {
  it('默认周期是 month', () => {
    const { activePeriod } = usePeriodFilter()
    expect(activePeriod.value).toBe('month')
  })

  it('selectPeriod 改变 activePeriod', () => {
    const { activePeriod, selectPeriod } = usePeriodFilter()

    selectPeriod('3month')
    expect(activePeriod.value).toBe('3month')

    selectPeriod('year')
    expect(activePeriod.value).toBe('year')
  })

  it('showCustomPopup 默认关闭', () => {
    const { showCustomPopup } = usePeriodFilter()
    expect(showCustomPopup.value).toBe(false)
  })

  it('selectPeriod("custom") 不自动显示 picker', () => {
    const { activePeriod, showCustomPopup, selectPeriod } = usePeriodFilter()

    selectPeriod('custom')
    expect(activePeriod.value).toBe('custom')
    // selectPeriod 只改状态，不弹 picker；openCustom 才弹
    expect(showCustomPopup.value).toBe(false)
  })

  it('openCustom 显示 picker 并重置步骤', () => {
    const { showCustomPopup, pickStep, openCustom } = usePeriodFilter()

    openCustom()

    expect(showCustomPopup.value).toBe(true)
    expect(pickStep.value).toBe('start')
  })

  describe('timeRange', () => {
    it('month 返回当月起止', () => {
      const { timeRange, selectPeriod } = usePeriodFilter()
      selectPeriod('month')

      const now = new Date()
      const expectedStart = new Date(now.getFullYear(), now.getMonth(), 1)

      expect(timeRange.value.start_time).toBe(Math.floor(expectedStart.getTime() / 1000))
      expect(timeRange.value.start_month).toBe(now.getMonth() + 1)
      expect(timeRange.value.start_year).toBe(now.getFullYear())
    })

    it('year 返回当年起止', () => {
      const { timeRange, selectPeriod } = usePeriodFilter()
      selectPeriod('year')

      const now = new Date()
      expect(timeRange.value.start_year).toBe(now.getFullYear())
      expect(timeRange.value.start_month).toBe(1)
    })

    it('3month 返回近3月起止', () => {
      const { timeRange, selectPeriod } = usePeriodFilter()
      selectPeriod('3month')

      const now = new Date()
      const expectedStart = new Date(now.getFullYear(), now.getMonth() - 2, 1)
      expect(timeRange.value.start_time).toBe(Math.floor(expectedStart.getTime() / 1000))
    })

    it('6month 返回近6月起止', () => {
      const { timeRange, selectPeriod } = usePeriodFilter()
      selectPeriod('6month')

      const now = new Date()
      const expectedStart = new Date(now.getFullYear(), now.getMonth() - 5, 1)
      expect(timeRange.value.start_time).toBe(Math.floor(expectedStart.getTime() / 1000))
    })
  })

  describe('onPickerConfirm', () => {
    it('第一步确认后切换到 end 步骤', () => {
      const { pickStep, onPickerConfirm } = usePeriodFilter()

      onPickerConfirm({ selectedValues: [2024, 6] })

      expect(pickStep.value).toBe('end')
    })

    it('第二步确认后设置 custom 日期范围', () => {
      const { activePeriod, showCustomPopup, customStartDate, customEndDate, onPickerConfirm } =
        usePeriodFilter()

      // 第一步：选起始月
      onPickerConfirm({ selectedValues: [2024, 1] })
      // 第二步：选结束月
      onPickerConfirm({ selectedValues: [2024, 6] })

      expect(activePeriod.value).toBe('custom')
      expect(showCustomPopup.value).toBe(false)
      expect(customStartDate.value.getFullYear()).toBe(2024)
      expect(customStartDate.value.getMonth()).toBe(0) // 1月 = 0
      expect(customEndDate.value.getFullYear()).toBe(2024)
      expect(customEndDate.value.getMonth()).toBe(5) // 6月 = 5
    })
  })

  it('periods 包含四个预设选项', () => {
    const { periods } = usePeriodFilter()
    expect(periods).toHaveLength(4)
    expect(periods.map((p) => p.key)).toEqual(['month', '3month', '6month', 'year'])
  })

  it('onCancelCustom 关闭 picker', () => {
    const { showCustomPopup, openCustom, onCancelCustom } = usePeriodFilter()

    openCustom()
    expect(showCustomPopup.value).toBe(true)

    onCancelCustom()
    expect(showCustomPopup.value).toBe(false)
  })
})
