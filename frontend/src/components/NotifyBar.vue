<script setup lang="ts">
import { notifyState, remove } from '../lib/feedback'

const colorMap: Record<string, string> = {
  success: 'var(--color-success)',
  error: 'var(--color-danger)',
  tip: 'var(--color-info)',
}
</script>

<template>
  <Teleport to="body">
    <div class="notify-bar__wrapper">
      <div
        v-for="item in notifyState.items"
        :key="item.id"
        @click="remove(item.id)"
        class="notify-bar__item"
        :style="{
          background: colorMap[item.type] || 'var(--color-text-primary)',
        }"
      >
        {{ item.message }}
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.notify-bar__wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10000;
}

.notify-bar__item {
  color: var(--color-surface);
  padding: var(--space-md) var(--space-lg);
  font-size: 14px;
  text-align: center;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
</style>
