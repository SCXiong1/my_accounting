<script setup lang="ts">
import { computed } from 'vue'
import { yuanToCents, centsToYuan } from '../core/format'

const props = defineProps<{ modelValue: number }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

// 用 string 表示元的值，方便输入
const yuanText = computed({
  get: () => (props.modelValue > 0 ? centsToYuan(props.modelValue) : ''),
  set: (val: string) => {
    emit('update:modelValue', yuanToCents(val))
  },
})
</script>

<template>
  <van-field
    v-model="yuanText"
    type="number"
    label="金额"
    placeholder="0.00"
    input-align="right"
  >
    <template #left-icon>
      <span style="font-size: 20px; font-weight: bold;">¥</span>
    </template>
  </van-field>
</template>
