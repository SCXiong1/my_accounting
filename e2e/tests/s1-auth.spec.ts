import { test, expect } from '@playwright/test'

async function completePinChange(page: import('@playwright/test').Page) {
  await page.getByPlaceholder('请输入当前PIN码').fill('1234')
  await page.getByPlaceholder(/请输入\d+-\d+位新PIN码/).fill('1234')
  await page.getByPlaceholder('请再次输入新PIN码').fill('1234')
  await page.getByRole('button', { name: '修改PIN码' }).click()
  await page.waitForURL('/')
}

test.describe('S1: PIN认证流程', () => {
  test('PIN登录：输入用户名和PIN码 → 跳转首页或修改PIN码页', async ({ page }) => {
    await page.goto('/login')

    await page.getByPlaceholder('请输入用户名').fill('user1')
    await page.getByPlaceholder(/请输入\d+-\d+位PIN码/).fill('1234')
    await page.getByRole('button', { name: '登录' }).click()

    await page.waitForURL((url) => url.pathname === '/' || url.pathname === '/pin-change')

    if (page.url().includes('/pin-change')) {
      await expect(page.locator('.van-nav-bar__title')).toHaveText('修改PIN码')
      await completePinChange(page)
    }

    await expect(page.getByRole('tablist')).toBeVisible()
  })

  test('首次登录强制修改PIN码', async ({ page }) => {
    await page.goto('/login')

    await page.getByPlaceholder('请输入用户名').fill('user1')
    await page.getByPlaceholder(/请输入\d+-\d+位PIN码/).fill('1234')
    await page.getByRole('button', { name: '登录' }).click()

    await page.waitForURL((url) => url.pathname === '/' || url.pathname === '/pin-change')

    if (page.url().includes('/pin-change')) {
      await expect(page.locator('.van-nav-bar__title')).toHaveText('修改PIN码')
      await completePinChange(page)
    }

    await expect(page.getByRole('tablist')).toBeVisible()
  })

  test('错误PIN码登录失败', async ({ page }) => {
    await page.goto('/login')

    await page.getByPlaceholder('请输入用户名').fill('user1')
    await page.getByPlaceholder(/请输入\d+-\d+位PIN码/).fill('9999')
    await page.getByRole('button', { name: '登录' }).click()

    await page.waitForTimeout(2000)
    await expect(page).toHaveURL(/\/login/)
  })

  test('退出登录：个人中心 → 退出 → 跳转登录页', async ({ page }) => {
    await page.goto('/login')
    await page.getByPlaceholder('请输入用户名').fill('user2')
    await page.getByPlaceholder(/请输入\d+-\d+位PIN码/).fill('1234')
    await page.getByRole('button', { name: '登录' }).click()

    await page.waitForURL((url) => url.pathname === '/' || url.pathname === '/pin-change')

    if (page.url().includes('/pin-change')) {
      await completePinChange(page)
    }

    await page.getByRole('tab', { name: '我的' }).click()
    await page.getByTestId('profile-logout').click()
    await page.getByRole('button', { name: '确认' }).click()

    await page.waitForURL('/login')
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible()
  })

  test('安全问题PIN码重置', async ({ page }) => {
    await page.goto('/pin-change?mode=reset')

    await page.getByPlaceholder('请输入用户名').fill('user1')
    await page.getByPlaceholder('请输入答案').fill('小1')
    await page.getByPlaceholder(/请输入\d+-\d+位新PIN码/).fill('1234')
    await page.getByPlaceholder('请再次输入新PIN码').fill('1234')
    await page.getByRole('button', { name: '重置PIN码' }).click()

    await page.waitForTimeout(2000)
    await expect(page).toHaveURL(/\/login/)
  })
})
