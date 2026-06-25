import { createCrudStore } from './createCrudStore'

export interface Category {
  id: number
  name: string
  icon: string
  color: string
  display_order: number
  transaction_count: number
  total_amount: number
}

export const useCategoryStore = createCrudStore<Category>({
  name: 'category',
  endpoint: '/v1/categories',
})
