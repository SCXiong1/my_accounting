<script setup lang="ts">
import { ref, computed } from 'vue'
import { showSuccess, showError, showTip } from '../lib/feedback'
import { useTagStore } from '../stores/tag'

const props = defineProps<{ modelValue: number[]; filteredTags?: { id: number; name: string }[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: number[]] }>()

const store = useTagStore()
const displayTags = computed(() => props.filteredTags ?? store.list)
const showDialog = ref(false)
const newTagName = ref('')
const adding = ref(false)

function toggleTag(id: number) {
  const tags = [...props.modelValue]
  const idx = tags.indexOf(id)
  if (idx > -1) {
    tags.splice(idx, 1)
  } else {
    tags.push(id)
  }
  emit('update:modelValue', tags)
}

async function open() {
  newTagName.value = ''
  showDialog.value = true
  if (!props.filteredTags && store.list.length === 0) {
    try {
      await store.fetchList()
    } catch {
      // 加载失败时弹窗仍然打开，显示空列表
    }
  }
}

async function addNewTag() {
  const name = newTagName.value.trim()
  if (!name) {
showTip('请输入标签名称')
    return
  }
  // 检查是否已存在同名标签
  const exists = store.list.find((t) => t.name === name)
  if (exists) {
    // 已存在则直接选中
    if (!props.modelValue.includes(exists.id)) {
      toggleTag(exists.id)
    }
    newTagName.value = ''
showTip('已选中已有标签')
    return
  }
  adding.value = true
  try {
    const tag = await store.create(name)
    // 将新标签加入 filteredTags 显示列表
    if (props.filteredTags && !props.filteredTags.some(t => t.id === tag.id)) {
      props.filteredTags.push({ id: tag.id, name: tag.name })
    }
    toggleTag(tag.id)
    newTagName.value = ''
showSuccess('标签已添加')
  } catch {
showError('创建失败')
  } finally {
    adding.value = false
  }
}

const selectedNames = computed(() => {
  if (props.modelValue.length === 0) return ''
  return props.modelValue
    .map((id) => displayTags.value.find((t) => t.id === id)?.name ?? store.list.find((t) => t.id === id)?.name)
    .filter(Boolean)
    .join('、')
})
</script>

<template>
  <van-field
    :model-value="selectedNames || '选择标签（可选）'"
    is-link
    readonly
    label="标签"
    :placeholder="selectedNames || '选择标签（可选）'"
    data-testid="tag-checkbox"
    @click="open"
  />
  <van-popup v-model:show="showDialog" position="bottom" round :style="{ height: '55%' }" data-testid="tag-checkbox__popup">
    <div class="tag-popup">
      <h4 class="tag-popup__title">选择标签</h4>

      <!-- 快速新增 -->
      <div class="tag-popup__add-row">
        <van-field
          v-model="newTagName"
          placeholder="输入新标签名"
          :border="true"
          class="tag-popup__add-input"
        />
        <van-button
          type="primary"
          size="small"
          :loading="adding"
          @click="addNewTag"
        >
          新增
        </van-button>
      </div>

      <!-- 已有标签列表 -->
      <div class="tag-popup__list">
        <div v-if="displayTags.length === 0" class="tag-popup__empty">
          {{ filteredTags ? '该分类下暂无标签' : '暂无标签，请先新增' }}
        </div>
        <van-checkbox-group :model-value="modelValue" data-testid="tag-checkbox__group">
          <van-cell
            v-for="tag in displayTags"
            :key="tag.id"
            :title="tag.name"
            clickable
            data-testid="tag-checkbox__cell"
            @click="toggleTag(tag.id)"
          >
            <template #right-icon>
              <van-checkbox :name="tag.id" />
            </template>
          </van-cell>
        </van-checkbox-group>
      </div>

      <div class="tag-popup__confirm">
        <van-button round block type="primary" @click="showDialog = false">确定</van-button>
      </div>
    </div>
  </van-popup>
</template>

<style scoped>
.tag-popup {
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tag-popup__title {
  margin: 0 0 var(--space-md);
}

.tag-popup__add-row {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.tag-popup__add-input {
  flex: 1;
}

.tag-popup__list {
  flex: 1;
  overflow-y: auto;
}

.tag-popup__empty {
  text-align: center;
  padding: var(--space-xl);
  color: var(--color-text-secondary);
}

.tag-popup__confirm {
  padding: var(--space-lg) 0;
}
</style>
