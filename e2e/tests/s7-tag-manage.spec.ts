import { testAuth, expect } from '../fixtures/auth'

const uid = Date.now()

testAuth.describe('S7: 标签管理', () => {
  testAuth('导航：/profile 点标签管理 → /tags', async ({ page }) => {
    await page.goto('/profile')
    // 等待页面加载
    await expect(page.getByRole('tab', { name: '我的' })).toBeVisible()

    await page.getByTestId('profile-nav-tags').click()

    await expect(page).toHaveURL(/\/tags/)
    await expect(page.getByText('标签管理')).toBeVisible()
  })

  testAuth('新增标签：点新增标签 → 填下午茶 → 确定', async ({ page }) => {
    await page.goto('/tags')
    await expect(page.getByText('标签管理')).toBeVisible()

    await page.getByRole('button', { name: '新增标签' }).click()

    // van-dialog 弹出
    const dialog = page.getByTestId('tag-manage-dialog')
    await expect(dialog).toBeVisible()

    // 填名称
    await page.getByPlaceholder('标签名称').fill(`下午茶_${uid}`)

    // 点确定
    await page.getByTestId('tag-manage-confirm').click()

    // 验证 tag 可见
    await expect(page.getByText(`下午茶_${uid}`)).toBeVisible()
  })

  testAuth('编辑标签：创建 → 点击 → 改名 → 确定', async ({ page }) => {
    await page.goto('/tags')
    await expect(page.getByText('标签管理')).toBeVisible()

    // 创建标签
    await page.getByRole('button', { name: '新增标签' }).click()
    const dialog = page.getByTestId('tag-manage-dialog')
    await expect(dialog).toBeVisible()
    await page.getByPlaceholder('标签名称').fill(`编辑A_${uid}`)
    await page.getByTestId('tag-manage-confirm').click()
    await expect(page.getByText(`编辑A_${uid}`)).toBeVisible()

    // 点击 tag 进入编辑
    await page
      .getByTestId('tag-manage-tag')
      .filter({ hasText: `编辑A_${uid}` })
      .click()
    await expect(dialog).toBeVisible()

    // 改名
    const nameInput = page.getByPlaceholder('标签名称')
    await nameInput.clear()
    await nameInput.fill(`编辑B_${uid}`)
    await page.getByTestId('tag-manage-confirm').click()

    // 验证新名称可见
    await expect(page.getByText(`编辑B_${uid}`)).toBeVisible()
  })

  testAuth('删除标签：点 close → 确认 → 消失', async ({ page }) => {
    await page.goto('/tags')
    await expect(page.getByText('标签管理')).toBeVisible()

    // 创建标签
    await page.getByRole('button', { name: '新增标签' }).click()
    const dialog = page.getByTestId('tag-manage-dialog')
    await expect(dialog).toBeVisible()
    await page.getByPlaceholder('标签名称').fill(`待删_${uid}`)
    await page.getByTestId('tag-manage-confirm').click()
    await expect(page.getByText(`待删_${uid}`)).toBeVisible()

    // 点击 tag 的 close 按钮
    const tag = page.getByTestId('tag-manage-tag').filter({ hasText: `待删_${uid}` })
    await tag.locator('.van-tag__close').click()

    // 确认删除对话框（由 showConfirmDialog 动态创建，无自定义 testid）
    await expect(page.getByText(/确定删除/)).toBeVisible()
    await page.getByRole('button', { name: '确认' }).click()

    // 验证消失
    await expect(
      page.getByTestId('tag-manage-tag').filter({ hasText: `待删_${uid}` }),
    ).not.toBeVisible()
  })
})
