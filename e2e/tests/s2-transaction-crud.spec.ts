import { testAuth, expect, loadMetadata } from '../fixtures/auth'
import { swipeCellLeft, selectPickerOption } from '../helpers/gestures'
import { apiClient } from '../helpers/api-client'

// 唯一后缀，避免多项目并行时数据冲突
const uid = Date.now()

function getCatId(metadata: ReturnType<typeof loadMetadata>, name: string): number {
  const cat = metadata.categories.find((c) => c.name === name)
  if (!cat) throw new Error(`分类 "${name}" 不存在于 metadata 中`)
  return cat.id
}

testAuth.describe('S2: 账单 CRUD', () => {
  testAuth('新增账单：填金额 → 选分类 → 选标签 → 填备注 → 提交', async ({ page }) => {
    const metadata = loadMetadata()
    const note = `新增测试_${uid}`

    // 先访问列表页建立历史，再进入新增页面
    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto('/transactions/add')
    await expect(page.getByText('新增支出')).toBeVisible()

    // 填写金额 25.50 元
    await page.getByPlaceholder('0.00').fill('25.50')

    // 选择分类：餐饮
    await page.getByRole('button', { name: /分类/ }).click()
    await selectPickerOption(page, '餐饮')

    // 选择标签：餐饮
    await page.getByRole('button', { name: /标签/ }).click()
    await page
      .getByTestId('tag-checkbox__popup')
      .getByTestId('tag-checkbox__cell')
      .filter({ hasText: '餐饮' })
      .click()
    await page.getByRole('button', { name: '确定' }).click()

    // 填写备注
    await page.getByPlaceholder('写点什么...').fill(note)

    // 提交
    await Promise.all([
      page.waitForURL('/transactions'),
      page.getByRole('button', { name: '记录支出' }).click(),
    ])

    // 验证新账单出现在列表中
    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    await expect(card).toBeVisible()
    await expect(card.getByTestId('transaction-card__amount')).toContainText('25.50')
  })

  testAuth('编辑分类：改餐饮 → 交通', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `编辑分类_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 1000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    await page.getByRole('button', { name: /分类/ }).click()
    await selectPickerOption(page, '交通')

    const saveBtn = page.getByRole('button', { name: '保存修改' })
    await saveBtn.waitFor({ state: 'visible' })
    await saveBtn.click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    await expect(card.getByTestId('transaction-card__category')).toContainText('交通')
  })

  testAuth('编辑标签：切换标签 餐饮 → 交通', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `编辑标签_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 2000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    await page.getByRole('button', { name: /标签/ }).click()
    await expect(page.getByText('选择标签')).toBeVisible()
    const popup = page.getByTestId('tag-checkbox__popup').getByTestId('tag-checkbox__group')
    await popup.getByTestId('tag-checkbox__cell').filter({ hasText: '餐饮' }).click()
    await popup.getByTestId('tag-checkbox__cell').filter({ hasText: '交通' }).click()
    await page.getByRole('button', { name: '确定' }).click()

    await page.getByRole('button', { name: '保存修改' }).click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    await expect(card.getByTestId('transaction-card__category')).toContainText('餐饮 · 交通')
  })

  testAuth('编辑备注：改备注为"测试备注"', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `编辑备注_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 3000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    const noteField = page.getByPlaceholder('写点什么...')
    await noteField.clear()
    await noteField.fill(`已修改_${uid}`)

    await page.getByRole('button', { name: '保存修改' }).click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page.getByTestId('transaction-card').filter({ hasText: `已修改_${uid}` })
    await expect(card).toBeVisible()
    await expect(card.getByTestId('transaction-card__amount')).toContainText('30.00')
  })

  testAuth('删除账单：左滑 → 删除 → 确认 → 验证消失', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `待删除_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 4000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText(note)).toBeVisible()

    // 左滑该账单卡片
    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    await swipeCellLeft(page, card)

    // 点击删除按钮（左滑后露出的按钮，限定在该卡片的 swipe-cell 内）
    const deleteBtn = page
      .getByTestId('transaction-list-swipe-cell')
      .filter({ has: card })
      .getByTestId('transaction-list-delete-btn')
    await deleteBtn.click()

    // 确认删除对话框
    await expect(page.getByText('确定删除这条支出记录吗？')).toBeVisible()
    await page.getByRole('button', { name: '确认' }).click()

    // 验证账单消失
    await expect(page.getByText(note)).not.toBeVisible()
  })

  // === 边界情况 ===

  testAuth('金额为 0 时提交应显示验证错误', async ({ page }) => {
    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto('/transactions/add')
    await expect(page.getByText('新增支出')).toBeVisible()

    await page.getByRole('button', { name: /分类/ }).click()
    await selectPickerOption(page, '餐饮')
    await page.getByRole('button', { name: '记录支出' }).click()

    await expect(page.getByText('请完善必填信息')).toBeVisible()
  })

  testAuth('超长备注（255 字符）可正常保存', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `超长备注_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 5000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    const longNote = `A${uid}_`.repeat(50).substring(0, 255)
    const noteField = page.getByPlaceholder('写点什么...')
    await noteField.clear()
    await noteField.fill(longNote)

    await page.getByRole('button', { name: '保存修改' }).click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page
      .getByTestId('transaction-card__note')
      .filter({ hasText: longNote.substring(0, 20) })
    await expect(card).toBeVisible()
  })

  testAuth('多标签选择', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `多标签_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 6000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    await page.getByRole('button', { name: /标签/ }).click()
    await expect(page.getByText('选择标签')).toBeVisible()
    await page
      .getByTestId('tag-checkbox__popup')
      .getByTestId('tag-checkbox__cell')
      .filter({ hasText: '交通' })
      .click()
    await page.getByRole('button', { name: '确定' }).click()

    await page.getByRole('button', { name: '保存修改' }).click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    const catText = await card.getByTestId('transaction-card__category').textContent()
    expect(catText).toContain('餐饮')
    expect(catText).toContain('交通')
  })

  testAuth('无标签提交', async ({ page, request }) => {
    const metadata = loadMetadata()
    const api = await apiClient(request)
    const note = `无标签_${uid}`

    const now = Math.floor(Date.now() / 1000)
    const createRes = await api.post('/api/v1/transactions', {
      amount: 7000,
      category_id: getCatId(metadata, '餐饮'),
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note,
    })
    const transaction = await createRes.json()

    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()
    await page.goto(`/transactions/${transaction.id}/edit`)
    await expect(page.getByText('编辑支出')).toBeVisible()

    await page.getByRole('button', { name: /标签/ }).click()
    await expect(page.getByText('选择标签')).toBeVisible()
    await page
      .getByTestId('tag-checkbox__popup')
      .getByTestId('tag-checkbox__cell')
      .filter({ hasText: '餐饮' })
      .click()
    await page.getByRole('button', { name: '确定' }).click()

    await page.getByRole('button', { name: '保存修改' }).click()
    await page.waitForURL('**/transactions', { timeout: 15000 })

    const card = page.getByTestId('transaction-card').filter({ hasText: note })
    await expect(card).toBeVisible()
    // 验证标签已移除：分类文本不含 " · " 标签分隔符
    await expect(card.getByTestId('transaction-card__category')).not.toContainText('·')
  })
})
