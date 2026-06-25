import { createCrudStore } from './createCrudStore'

export interface Tag {
  id: number
  name: string
  display_order: number
  transaction_count: number
}

export const useTagStore = createCrudStore<Tag>({
  name: 'tag',
  endpoint: '/v1/tags',
})
