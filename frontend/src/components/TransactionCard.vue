<script setup lang="ts">
import { computed } from 'vue'
import { formatAmount } from '../core/format'
import { formatShortDate } from '../core/time'
import type { ExpenseItem } from '../stores/expense'

const props = defineProps<{ expense: ExpenseItem }>()

const desc = computed(() => {
  const parts = [props.expense.category.name]
  if (props.expense.tags.length > 0) {
    parts.push(props.expense.tags.map(t => t.name).join('、'))
  }
  return parts.join(' · ')
})
</script>

<template>
  <div class="expense-card" data-testid="expense-card">
    <div
      class="expense-card__icon"
      :style="{ background: expense.category.color + '20', color: expense.category.color }"
    >
      {{ expense.category.icon }}
    </div>
    <div class="expense-card__info">
      <div class="expense-card__category" data-testid="expense-card__category">{{ desc }}</div>
      <div v-if="expense.note" class="expense-card__note" data-testid="expense-card__note">{{ expense.note }}</div>
      <div class="expense-card__time" data-testid="expense-card__time">{{ formatShortDate(expense.transaction_time) }}</div>
    </div>
    <div class="expense-card__amount" data-testid="expense-card__amount">
      {{ formatAmount(expense.amount) }}
    </div>
  </div>
</template>
