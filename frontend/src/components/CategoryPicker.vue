<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCategoryStore } from '../stores/category'

const props = defineProps<{ modelValue: number | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const store = useCategoryStore()
const showPicker = ref(false)

function catName(id: number): string {
  const cat = store.list.find((c) => c.id === id)
  return cat ? `${cat.icon} ${cat.name}` : '请选择分类'
}

const selectedName = computed(() => catName(props.modelValue as number))

const pickerColumns = computed(() =>
  store.list.map((cat) => ({
    text: `${cat.icon} ${cat.name}`,
    value: cat.id,
  }))
)

function onSelect(id: number) {
  const cat = store.list.find((c) => c.id === id)
  if (cat) {
    emit('update:modelValue', id)
  }
  showPicker.value = false
}

function open() {
  if (store.list.length === 0) {
    store.fetchList()
  }
  showPicker.value = true
}
</script>

<template>
  <van-field
    :model-value="selectedName"
    is-link
    readonly
    label="分类"
    placeholder="请选择分类"
    data-testid="category-picker"
    @click="open"
  />
  <van-popup v-model:show="showPicker" position="bottom" round data-testid="category-picker__popup">
    <van-picker
      :columns="pickerColumns"
      data-testid="category-picker__column"
      @confirm="({ selectedValues }: { selectedValues: number[] }) => onSelect(selectedValues[0])"
      @cancel="showPicker = false"
    />
  </van-popup>
</template>
