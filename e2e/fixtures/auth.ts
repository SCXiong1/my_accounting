import { test as base, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export interface TestMetadata {
  user: { id: number; username: string; nickname: string }
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

async function loginViaPage(context: import('@playwright/test').BrowserContext) {
  const page = await context.newPage()
  await page.goto('/login')
  await page.getByPlaceholder('请输入用户名').fill('user1')
  await page.getByPlaceholder(/请输入\d+-\d+位PIN码/).fill('1234')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL((url) => url.pathname === '/' || url.pathname === '/pin-change')

  if (page.url().includes('/pin-change')) {
    await page.getByPlaceholder('请输入当前PIN码').fill('1234')
    await page.getByPlaceholder(/请输入\d+-\d+位新PIN码/).fill('1234')
    await page.getByPlaceholder('请再次输入新PIN码').fill('1234')
    await page.getByRole('button', { name: '修改PIN码' }).click()
    await page.waitForURL('/')
  }

  await page.close()
}

export const testAuth = base.extend<{}>({
  context: async ({ browser }, use, testInfo) => {
    const context = await browser.newContext({
      ...testInfo.project.use,
    })
    await loginViaPage(context)
    await use(context)
    await context.close()
  },
})

export { expect }
