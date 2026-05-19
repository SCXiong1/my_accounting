<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCategoryStore } from '../stores/category'

const props = defineProps<{ modelValue: number | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const store = useCategoryStore()
const showPicker = ref(false)

function catName(id: number): string {
  const cat = store.list.find((c) => c.id === id)
  return cat ? `${cat.icon} ${cat.name}` : '请选择分类'
}

const selectedName = ref(catName(props.modelValue as number))

watch(() => props.modelValue, (id) => {
  selectedName.value = catName(id as number)
})

const pickerColumns = computed(() =>
  store.list.map((cat) => ({
    text: `${cat.icon} ${cat.name}`,
    value: cat.id,
  }))
)

function onSelect(id: number) {
  const cat = store.list.find((c) => c.id === id)
  if (cat) {
    selectedName.value = `${cat.icon} ${cat.name}`
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
    @click="open"
  />
  <van-popup v-model:show="showPicker" position="bottom" round>
    <van-picker
      :columns="pickerColumns"
      @confirm="({ selectedValues }: { selectedValues: number[] }) => onSelect(selectedValues[0])"
      @cancel="showPicker = false"
    />
  </van-popup>
</template>
