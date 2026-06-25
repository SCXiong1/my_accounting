import { test as base, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export interface TestMetadata {
  user: { id: number; username: string; nickname: string }
  token: string
  categories: { id: number; name: string }[]
  tags: { id: number; name: string }[]
  transactions: { id: number; amount: number; note: string; category_id: number; tag_ids: number[] }[]
}

export function loadMetadata(): TestMetadata {
  const metadataPath = path.join(__dirname, '..', 'test-metadata.json')
  if (!fs.existsSync(metadataPath)) {
    throw new Error('test-metadata.json 不存在，请先运行 global-setup')
  }
  return JSON.parse(fs.readFileSync(metadataPath, 'utf-8'))
}

export const testNoAuth = base.extend<{}>({
  context: async ({ browser }, use, testInfo) => {
    const context = await browser.newContext({
      ...testInfo.project.use,
      storageState: { cookies: [], origins: [] },
    })
    await use(context)
    await context.close()
  },
})

const storageStatePath = path.join(__dirname, '..', 'storage-state.json')

export const testAuth = base.extend<{}>({
  context: async ({ browser }, use, testInfo) => {
    const context = await browser.newContext({
      ...testInfo.project.use,
      storageState: storageStatePath,
    })
    await use(context)
    await context.close()
  },
})

export { expect }
