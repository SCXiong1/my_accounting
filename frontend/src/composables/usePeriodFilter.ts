import { ref, computed } from 'vue'

export type Period = 'month' | '3month' | '6month' | 'year' | 'custom'

const PERIOD_OPTIONS: { key: Period; label: string }[] = [
  { key: 'month', label: '本月' },
  { key: '3month', label: '近3月' },
  { key: '6month', label: '近6月' },
  { key: 'year', label: '今年' },
]

export function usePeriodFilter() {
  const activePeriod = ref<Period>('month')
  const showCustomPopup = ref(false)
  const pickStep = ref<'start' | 'end'>('start')
  const customStartDate = ref(new Date())
  const customEndDate = ref(new Date())
  const pickerValue = ref<string[]>([
    String(new Date().getFullYear()),
    String(new Date().getMonth() + 1),
  ])
  const pendingStart = ref<Date | null>(null)

  const periods = PERIOD_OPTIONS

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
        end = customEndDate.value
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

  function selectPeriod(p: Period) {
    activePeriod.value = p
  }

  function openCustom() {
    pendingStart.value = null
    pickStep.value = 'start'
    pickerValue.value = [
      String(customStartDate.value.getFullYear()),
      String(customStartDate.value.getMonth() + 1),
    ]
    showCustomPopup.value = true
  }

  function onPickerConfirm({ selectedValues }: { selectedValues: number[] }) {
    if (pickStep.value === 'start') {
      pendingStart.value = new Date(selectedValues[0], selectedValues[1] - 1, 1)
      pickStep.value = 'end'
      pickerValue.value = [
        String(customEndDate.value.getFullYear()),
        String(customEndDate.value.getMonth() + 1),
      ]
    } else {
      const endDate = new Date(selectedValues[0], selectedValues[1], 0, 23, 59, 59)
      const startDate = pendingStart.value!
      customStartDate.value = startDate
      customEndDate.value =
        endDate < startDate
          ? new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0, 23, 59, 59)
          : endDate
      showCustomPopup.value = false
      activePeriod.value = 'custom'
    }
  }

  function onCancelCustom() {
    showCustomPopup.value = false
  }

  return {
    activePeriod,
    periods,
    timeRange,
    showCustomPopup,
    pickStep,
    pickerValue,
    customStartDate,
    customEndDate,
    selectPeriod,
    openCustom,
    onPickerConfirm,
    onCancelCustom,
  }
}
