<script setup lang="ts">
import { computed } from 'vue'
import { formatAmount } from '../core/format'
import { formatShortDate } from '../core/time'
import type { TransactionItem } from '../stores/transaction'

const props = defineProps<{ transaction: TransactionItem }>()

const desc = computed(() => {
  const parts = [props.transaction.category.name]
  if (props.transaction.tags.length > 0) {
    parts.push(props.transaction.tags.map((t) => t.name).join('、'))
  }
  return parts.join(' · ')
})
</script>

<template>
  <div class="transaction-card" data-testid="transaction-card">
    <div
      class="transaction-card__icon"
      :style="{ background: transaction.category.color + '20', color: transaction.category.color }"
    >
      {{ transaction.category.icon }}
    </div>
    <div class="transaction-card__info">
      <div class="transaction-card__category" data-testid="transaction-card__category">
        {{ desc }}
      </div>
      <div
        v-if="transaction.note"
        class="transaction-card__note"
        data-testid="transaction-card__note"
      >
        {{ transaction.note }}
      </div>
      <div class="transaction-card__time" data-testid="transaction-card__time">
        {{ formatShortDate(transaction.transaction_time) }}
      </div>
    </div>
    <div class="transaction-card__amount" data-testid="transaction-card__amount">
      {{ formatAmount(transaction.amount) }}
    </div>
  </div>
</template>
