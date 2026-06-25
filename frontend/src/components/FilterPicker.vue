<script setup lang="ts">
interface ColumnItem {
  text: string
  value: number
}

defineProps<{
  show: boolean
  columns: ColumnItem[]
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  select: [value: number]
}>()
</script>

<template>
  <van-popup :show="show" position="bottom" round @update:show="emit('update:show', $event)">
    <van-picker
      :columns="columns"
      @confirm="
        ({ selectedValues }: { selectedValues: number[] }) => {
          emit('select', selectedValues[0])
          emit('update:show', false)
        }
      "
      @cancel="emit('update:show', false)"
    />
  </van-popup>
</template>
