import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { buildQueryParams, createCancellableRequest } from '../lib/api'

export interface CategoryStatItem {
  category_id: number
  category_name: string
  category_icon: string
  category_color: string
  total_amount: number
  percentage: number
  transaction_count: number
}

export interface TagStatItem {
  tag_id: number
  tag_name: string
  total_amount: number
  percentage: number
  transaction_count: number
}

export interface MonthlyTagDetail {
  tag_id: number
  tag_name: string
  amount: number
}

export interface MonthlyStatItem {
  year: number
  month: number
  total_amount: number
  transaction_count: number
  by_category: {
    category_id: number
    category_name: string
    category_icon: string
    category_color: string
    amount: number
  }[]
  by_tag: MonthlyTagDetail[]
}

export const useStatisticsStore = defineStore('statistics', () => {
  const categoryStats = ref<CategoryStatItem[]>([])
  const tagStats = ref<TagStatItem[]>([])
  const monthlyStats = ref<MonthlyStatItem[]>([])
  const overview = ref({ today: 0, this_week: 0, this_month: 0, this_year: 0 })

  // Independent loading states for each fetch function
  const overviewLoading = ref(false)
  const categoryLoading = ref(false)
  const tagLoading = ref(false)
  const monthlyLoading = ref(false)

  // Computed aggregate loading state
  const loading = computed(
    () =>
      overviewLoading.value || categoryLoading.value || tagLoading.value || monthlyLoading.value,
  )

  // Request cancellation for each fetch type
  const categoryRequest = createCancellableRequest()
  const tagRequest = createCancellableRequest()
  const monthlyRequest = createCancellableRequest()

  // Sequence counters to guard stale finally blocks
  let catSeq = 0
  let tagSeq = 0
  let monthSeq = 0

  async function fetchOverview() {
    overviewLoading.value = true
    try {
      const res = await api.get('/v1/statistics/overview')
      overview.value = res.data
    } finally {
      overviewLoading.value = false
    }
  }

  async function fetchByCategory(start_time?: number, end_time?: number, tag_ids?: string) {
    const mySeq = ++catSeq
    categoryLoading.value = true
    try {
      const data = await categoryRequest.execute(async (signal) => {
        const params = buildQueryParams({ start_time, end_time, tag_ids })
        const res = await api.get('/v1/statistics/by_category', { params, signal })
        return res.data
      })
      if (mySeq !== catSeq) return
      categoryStats.value = data
    } finally {
      if (mySeq === catSeq) categoryLoading.value = false
    }
  }

  async function fetchByTag(start_time?: number, end_time?: number, category_ids?: string) {
    const mySeq = ++tagSeq
    tagLoading.value = true
    try {
      const data = await tagRequest.execute(async (signal) => {
        const params = buildQueryParams({ start_time, end_time, category_ids })
        const res = await api.get('/v1/statistics/by_tag', { params, signal })
        return res.data
      })
      if (mySeq !== tagSeq) return
      tagStats.value = data
    } finally {
      if (mySeq === tagSeq) tagLoading.value = false
    }
  }

  async function fetchMonthly(
    start_year?: number,
    start_month?: number,
    end_year?: number,
    end_month?: number,
    category_ids?: string,
    tag_ids?: string,
  ) {
    const mySeq = ++monthSeq
    monthlyLoading.value = true
    try {
      const data = await monthlyRequest.execute(async (signal) => {
        const params = buildQueryParams({
          start_year,
          start_month,
          end_year,
          end_month,
          category_ids,
          tag_ids,
        })
        const res = await api.get('/v1/statistics/monthly', { params, signal })
        return res.data
      })
      if (mySeq !== monthSeq) return
      monthlyStats.value = data
    } finally {
      if (mySeq === monthSeq) monthlyLoading.value = false
    }
  }

  return {
    categoryStats,
    tagStats,
    monthlyStats,
    overview,
    loading,
    overviewLoading,
    categoryLoading,
    tagLoading,
    monthlyLoading,
    fetchOverview,
    fetchByCategory,
    fetchByTag,
    fetchMonthly,
  }
})
