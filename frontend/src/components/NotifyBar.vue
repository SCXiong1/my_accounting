<script setup lang="ts">
import { notifyState, remove } from '../lib/feedback'

const colorMap: Record<string, string> = {
  success: '#07c160',
  error: '#ee0a24',
  tip: '#1989fa',
}
</script>

<template>
  <Teleport to="body">
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 10000;">
      <div
        v-for="item in notifyState.items"
        :key="item.id"
        @click="remove(item.id)"
        :style="{
          background: colorMap[item.type] || '#323233',
          color: '#fff',
          padding: '12px 16px',
          fontSize: '14px',
          textAlign: 'center',
          cursor: 'pointer',
          borderBottom: '1px solid rgba(255,255,255,0.15)',
        }"
      >
        {{ item.message }}
      </div>
    </div>
  </Teleport>
</template>
