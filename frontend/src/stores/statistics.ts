import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

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

export interface MonthlyStatItem {
  year: number
  month: number
  total_amount: number
  transaction_count: number
  by_category: { category_id: number; category_name: string; category_icon: string; category_color: string; amount: number }[]
}

export const useStatisticsStore = defineStore('statistics', () => {
  const categoryStats = ref<CategoryStatItem[]>([])
  const tagStats = ref<TagStatItem[]>([])
  const monthlyStats = ref<MonthlyStatItem[]>([])
  const loading = ref(false)

  async function fetchByCategory(start_time?: number, end_time?: number, tag_ids?: string) {
    loading.value = true
    try {
      const params: Record<string, string> = {}
      if (start_time) params.start_time = String(start_time)
      if (end_time) params.end_time = String(end_time)
      if (tag_ids) params.tag_ids = tag_ids
      const res = await api.get('/v1/statistics/by_category', { params })
      categoryStats.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchByTag(start_time?: number, end_time?: number, category_ids?: string) {
    loading.value = true
    try {
      const params: Record<string, string> = {}
      if (start_time) params.start_time = String(start_time)
      if (end_time) params.end_time = String(end_time)
      if (category_ids) params.category_ids = category_ids
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
      const params: Record<string, string> = {}
      if (start_year) params.start_year = String(start_year)
      if (start_month) params.start_month = String(start_month)
      if (end_year) params.end_year = String(end_year)
      if (end_month) params.end_month = String(end_month)
      if (category_ids) params.category_ids = category_ids
      if (tag_ids) params.tag_ids = tag_ids
      const res = await api.get('/v1/statistics/monthly', { params })
      monthlyStats.value = res.data
    } finally {
      loading.value = false
    }
  }

  return { categoryStats, tagStats, monthlyStats, loading, fetchByCategory, fetchByTag, fetchMonthly }
})
