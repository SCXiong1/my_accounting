<script setup lang="ts">
import { watch } from 'vue'
import { usePeriodFilter } from '../composables/usePeriodFilter'

export interface TimeRange {
  start_time: number
  end_time: number
  start_year: number
  start_month: number
  end_year: number
  end_month: number
}

defineProps<{ testIdPrefix?: string }>()

const {
  activePeriod,
  periods,
  timeRange,
  showCustomPopup,
  pickStep,
  pickerValue,
  selectPeriod,
  openCustom,
  onPickerConfirm,
  onCancelCustom,
} = usePeriodFilter()

const emit = defineEmits<{
  change: [timeRange: TimeRange]
}>()

watch(timeRange, (range) => {
  emit('change', range)
}, { immediate: true })
</script>

<template>
  <div class="filter-bar">
    <van-button
      v-for="p in periods"
      :key="p.key"
      :type="activePeriod === p.key ? 'primary' : 'default'"
      size="small"
      round
      :data-testid="`${testIdPrefix ?? 'period'}-btn`"
      @click="selectPeriod(p.key)"
    >
      {{ p.label }}
    </van-button>
    <van-button
      :type="activePeriod === 'custom' ? 'primary' : 'default'"
      size="small"
      round
      @click="openCustom"
    >
      自定义
    </van-button>
  </div>

  <van-popup v-model:show="showCustomPopup" position="bottom" round>
    <div class="custom-popup">
      <div class="custom-popup__title">
        {{ pickStep === 'start' ? '选择开始月份' : '选择结束月份' }}
      </div>
      <van-date-picker
        :key="pickStep"
        v-model="pickerValue"
        :columns-type="['year', 'month']"
        @confirm="onPickerConfirm"
        @cancel="onCancelCustom"
      />
    </div>
  </van-popup>
</template>

<style scoped>
.custom-popup {
  padding: var(--space-lg);
}

.custom-popup__title {
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: var(--space-md);
}
</style>
