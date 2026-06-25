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
  categories: SeedCategory[]
  tags: SeedTag[]
  transactions: SeedTransaction[]
}

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use
  const apiBase = baseURL!.replace(/:\d+/, ':8080')
  const storageStatePath = path.join(__dirname, 'storage-state.json')
  const metadataPath = path.join(__dirname, 'test-metadata.json')

  for (const f of [storageStatePath, metadataPath]) {
    if (fs.existsSync(f)) fs.unlinkSync(f)
  }

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

  const loginRes = await fetch(`${apiBase}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'user1', pin: '1234' }),
    credentials: 'include',
  })
  if (!loginRes.ok) throw new Error(`登录失败: ${loginRes.status} ${await loginRes.text()}`)
  const { user } = await loginRes.json()
  const cookies = loginRes.headers.getSetCookie()

  const cookieHeader = cookies.map((c) => c.split(';')[0]).join('; ')

  console.log(`[global-setup] Login successful, user: ${user.username}, pin_changed: ${user.pin_changed}`)

  const changePinRes = await fetch(`${apiBase}/api/auth/change-pin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Cookie: cookieHeader,
    },
    body: JSON.stringify({ current_pin: '1234', new_pin: '1234' }),
  })
  if (!changePinRes.ok) {
    const text = await changePinRes.text()
    console.log(`[global-setup] Warning: Failed to mark PIN as changed: ${changePinRes.status} ${text}`)
  } else {
    console.log(`[global-setup] PIN marked as changed successfully`)
  }

  const loginRes2 = await fetch(`${apiBase}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'user2', pin: '1234' }),
    credentials: 'include',
  })
  if (loginRes2.ok) {
    const cookies2 = loginRes2.headers.getSetCookie()
    const cookieHeader2 = cookies2.map((c) => c.split(';')[0]).join('; ')
    const changePinRes2 = await fetch(`${apiBase}/api/auth/change-pin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookieHeader2,
      },
      body: JSON.stringify({ current_pin: '1234', new_pin: '1234' }),
    })
    if (!changePinRes2.ok) {
      console.log(`[global-setup] Warning: Failed to mark user2 PIN as changed`)
    } else {
      console.log(`[global-setup] user2 PIN marked as changed successfully`)
    }
  }

  const authHeaders = {
    'Content-Type': 'application/json',
    Cookie: cookieHeader,
  }

  const catRes = await fetch(`${apiBase}/api/v1/categories`, { headers: authHeaders })
  if (!catRes.ok) throw new Error(`获取分类失败: ${catRes.status}`)
  const categories = (await catRes.json()) as Array<{ id: number; name: string }>
  const catMap = Object.fromEntries(categories.map((c) => [c.name, c.id]))

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

  const storageState = {
    cookies: cookies.map((c) => {
      const parts = c.split(';').map((p) => p.trim())
      const [nameValue, ...attrs] = parts
      const [name, value] = nameValue.split('=')
      const cookie: Record<string, unknown> = {
        name,
        value,
        domain: 'localhost',
        path: '/',
        sameSite: 'Lax' as const,
      }
      for (const attr of attrs) {
        const [key, val] = attr.split('=')
        if (key.toLowerCase() === 'expires') cookie.expires = new Date(val).getTime() / 1000
        if (key.toLowerCase() === 'httponly') cookie.httpOnly = true
      }
      return cookie
    }),
    origins: [],
  }
  fs.writeFileSync(storageStatePath, JSON.stringify(storageState, null, 2))

  const metadata: TestMetadata = { user, categories, tags, transactions }
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2))

  console.log(
    `[global-setup] 用户: ${user.username}, 标签: ${tags.length}, 账单: ${transactions.length}`,
  )
}

export default globalSetup
