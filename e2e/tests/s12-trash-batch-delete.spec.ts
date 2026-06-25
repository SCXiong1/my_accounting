import { testAuth, expect } from '../fixtures/auth'
import { apiClient } from '../helpers/api-client'

testAuth.describe('S12: 回收站批量删除', () => {
  testAuth('批量删除按钮可见，可进入选择模式', async ({ page }) => {
    await page.goto('/trash')
    await expect(page.getByText('回收站')).toBeVisible()

    // 批量删除按钮存在
    const batchBtn = page.getByTestId('trash-select-mode')
    await expect(batchBtn).toBeVisible()
    await expect(batchBtn).toHaveText('批量删除')

    // 点击进入选择模式
    await batchBtn.click()

    // 底部操作栏出现
    await expect(page.getByTestId('trash-batch-bar')).toBeVisible()
    // 按钮文字变为"取消"
    await expect(batchBtn).toHaveText('取消')
  })

  testAuth('选择模式下显示复选框，可选择和取消', async ({ page, request }) => {
    const api = await apiClient(request)

    // 创建并删除一条支出
    const cats = await (await api.get('/api/v1/categories')).json()
    const res = await api.post('/api/v1/transactions', {
      amount: 5000,
      category_id: cats[0].id,
      tag_ids: [],
      transaction_time: Math.floor(Date.now() / 1000),
      note: '批量删除测试',
    })
    const transaction = await res.json()
    await api.delete(`/api/v1/transactions/${transaction.id}`)

    await page.goto('/trash')
    await expect(page.getByText('回收站')).toBeVisible()

    // 进入选择模式
    await page.getByTestId('trash-select-mode').click()

    // 复选框可见
    const checkboxes = page.getByTestId('trash-checkbox')
    await expect(checkboxes.first()).toBeVisible()

    // 点击选中
    await checkboxes.first().click()

    // 底部显示已选数量
    await expect(page.getByTestId('trash-batch-bar')).toContainText('1/')
  })

  testAuth('未选择时删除按钮禁用', async ({ page }) => {
    await page.goto('/trash')
    await expect(page.getByText('回收站')).toBeVisible()

    // 进入选择模式
    await page.getByTestId('trash-select-mode').click()

    // 删除按钮应禁用
    const deleteBtn = page.getByTestId('trash-batch-delete')
    await expect(deleteBtn).toBeDisabled()
  })

  testAuth('批量删除需确认对话框', async ({ page, request }) => {
    const api = await apiClient(request)

    // 创建并删除一条支出
    const cats = await (await api.get('/api/v1/categories')).json()
    const res = await api.post('/api/v1/transactions', {
      amount: 7000,
      category_id: cats[0].id,
      tag_ids: [],
      transaction_time: Math.floor(Date.now() / 1000),
      note: '确认对话框测试',
    })
    const transaction = await res.json()
    await api.delete(`/api/v1/transactions/${transaction.id}`)

    await page.goto('/trash')
    await expect(page.getByText('回收站')).toBeVisible()

    // 进入选择模式，选中一条
    await page.getByTestId('trash-select-mode').click()
    await page.getByTestId('trash-checkbox').first().click()

    // 点击删除
    await page.getByTestId('trash-batch-delete').click()

    // 确认对话框出现
    await expect(page.getByText('确定永久删除')).toBeVisible()
    await expect(page.getByText('此操作不可撤销')).toBeVisible()
  })
})
