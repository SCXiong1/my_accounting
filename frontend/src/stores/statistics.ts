import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { buildQueryParams } from '../lib/api'

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
  by_category: { category_id: number; category_name: string; category_icon: string; category_color: string; amount: number }[]
  by_tag: MonthlyTagDetail[]
}

export const useStatisticsStore = defineStore('statistics', () => {
  const categoryStats = ref<CategoryStatItem[]>([])
  const tagStats = ref<TagStatItem[]>([])
  const monthlyStats = ref<MonthlyStatItem[]>([])
  const loading = ref(false)

  async function fetchByCategory(start_time?: number, end_time?: number, tag_ids?: string) {
    loading.value = true
    try {
      const params = buildQueryParams({ start_time, end_time, tag_ids })
      const res = await api.get('/v1/statistics/by_category', { params })
      categoryStats.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchByTag(start_time?: number, end_time?: number, category_ids?: string) {
    loading.value = true
    try {
      const params = buildQueryParams({ start_time, end_time, category_ids })
      const res = await api.get('/v1/statistics/by_tag', { params })
      tagStats.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchMonthly(
    start_year?: number, start_month?: number,
    end_year?: number, end_month?: number,
    category_ids?: string, tag_ids?: string,
  ) {
    loading.value = true
    try {
      const params = buildQueryParams({ start_year, start_month, end_year, end_month, category_ids, tag_ids })
      const res = await api.get('/v1/statistics/monthly', { params })
      monthlyStats.value = res.data
    } finally {
      loading.value = false
    }
  }

  return { categoryStats, tagStats, monthlyStats, loading, fetchByCategory, fetchByTag, fetchMonthly }
})
