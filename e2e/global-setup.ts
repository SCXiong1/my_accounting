import { FullConfig } from '@playwright/test'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

interface SeedUser {
  id: number
  username: string
  nickname: string
}

interface SeedCategory {
  id: number
  name: string
}

interface SeedTag {
  id: number
  name: string
}

interface SeedTransaction {
  id: number
  amount: number
  note: string
  category_id: number
  tag_ids: number[]
}

interface TestMetadata {
  user: SeedUser
  token: string
  categories: SeedCategory[]
  tags: SeedTag[]
  transactions: SeedTransaction[]
}

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use
  const apiBase = baseURL!.replace(/:\d+/, ':8080')
  const storageStatePath = path.join(__dirname, 'storage-state.json')
  const metadataPath = path.join(__dirname, 'test-metadata.json')

  // 清理旧文件
  for (const f of [storageStatePath, metadataPath]) {
    if (fs.existsSync(f)) fs.unlinkSync(f)
  }

  // 等待后端健康检查
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`${apiBase}/api/health`)
      if (res.ok) break
    } catch {
      /* not ready */
    }
    if (i === 29) throw new Error('后端服务未就绪')
    await new Promise((r) => setTimeout(r, 2000))
  }

  // 1. 注册测试用户
  const ts = Date.now()
  const regRes = await fetch(`${apiBase}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: `e2e_seed_${ts}`,
      email: `e2e_seed_${ts}@test.com`,
      password: 'E2eSeed123',
      nickname: '测试用户',
    }),
  })
  if (!regRes.ok) throw new Error(`注册失败: ${regRes.status} ${await regRes.text()}`)
  const { token, user } = await regRes.json()

  const authHeaders = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }

  // 2. 获取注册时自动创建的分类列表
  const catRes = await fetch(`${apiBase}/api/v1/categories`, { headers: authHeaders })
  if (!catRes.ok) throw new Error(`获取分类失败: ${catRes.status}`)
  const categories = (await catRes.json()) as Array<{ id: number; name: string }>
  const catMap = Object.fromEntries(categories.map((c) => [c.name, c.id]))

  // 3. 创建 4 个标签
  const tagNames = ['餐饮', '交通', '购物', '娱乐']
  const tags: SeedTag[] = []
  for (const name of tagNames) {
    const res = await fetch(`${apiBase}/api/v1/tags`, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error(`创建标签失败: ${res.status}`)
    tags.push(await res.json())
  }

  // 4. 创建 5 条样本账单（金额为分）
  const now = Math.floor(Date.now() / 1000)
  const transactionData = [
    {
      amount: 3500,
      note: '午餐',
      category_id: catMap['餐饮'],
      tag_ids: [tags[0].id, tags[1].id],
      days_ago: 0,
    },
    {
      amount: 15000,
      note: '打车',
      category_id: catMap['交通'],
      tag_ids: [tags[1].id],
      days_ago: 0,
    },
    {
      amount: 29900,
      note: '买衣服',
      category_id: catMap['购物'],
      tag_ids: [tags[2].id],
      days_ago: 1,
    },
    {
      amount: 8800,
      note: '电影票',
      category_id: catMap['娱乐'],
      tag_ids: [tags[3].id],
      days_ago: 2,
    },
    { amount: 5600, note: '外卖', category_id: catMap['餐饮'], tag_ids: [tags[0].id], days_ago: 3 },
  ]

  const transactions: SeedTransaction[] = []
  for (const d of transactionData) {
    const res = await fetch(`${apiBase}/api/v1/transactions`, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({
        amount: d.amount,
        category_id: d.category_id,
        tag_ids: d.tag_ids,
        transaction_time: now - d.days_ago * 86400,
        timezone_offset: 480,
        note: d.note,
      }),
    })
    if (!res.ok) throw new Error(`创建账单失败: ${res.status} ${await res.text()}`)
    transactions.push(await res.json())
  }

  // 4. 导出 storageState（含 JWT token）
  const storageState = {
    cookies: [],
    origins: [
      {
        origin: baseURL!,
        localStorage: [
          { name: 'ezexpense_token', value: token },
          { name: 'user', value: JSON.stringify(user) },
        ],
      },
    ],
  }
  fs.writeFileSync(storageStatePath, JSON.stringify(storageState, null, 2))

  // 6. 导出测试元数据
  const metadata: TestMetadata = { user, token, categories, tags, transactions }
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2))

  console.log(
    `[global-setup] 用户: ${user.username}, 标签: ${tags.length}, 账单: ${transactions.length}`,
  )
}

export default globalSetup
