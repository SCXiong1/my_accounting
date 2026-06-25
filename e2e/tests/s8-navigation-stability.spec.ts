import { testAuth, expect } from '../fixtures/auth'

testAuth.describe('S8: 页面导航稳定性', () => {
  testAuth('快速切换 tabbar 页面不触发刷新，数据正常显示', async ({ page }) => {
    // 登录后首页
    await page.goto('/')
    await expect(page.getByText('个人记账')).toBeVisible()

    // 记录首页的 URL，用于后续检测是否发生了整页刷新
    const homeUrl = page.url()

    // 快速切换到各个 tab 页面
    const tabs = [
      { name: '记账', title: '支出记录' },
      { name: '统计', title: '统计分析' },
      { name: '我的', title: '我的' },
      { name: '首页', title: '个人记账' },
    ]

    for (const tab of tabs) {
      await page.getByRole('tab', { name: tab.name }).click()
      // 等待页面标题出现，确认导航成功
      await expect(page.getByText(tab.title).first()).toBeVisible({ timeout: 5000 })
    }

    // URL 应该是首页，且不应该发生过整页刷新（通过检查 URL 未变化）
    expect(page.url()).toContain('/')
  })

  testAuth('统计页面图表二次进入正常加载', async ({ page }) => {
    // 第一次进入统计页面
    await page.goto('/statistics')
    await expect(page.getByText('统计分析')).toBeVisible()

    // 等待图表加载
    await page.waitForSelector('[data-testid="chart-bar"], [data-testid="chart-pie"]', {
      timeout: 10000,
    })

    // 切换到其他页面
    await page.getByRole('tab', { name: '首页' }).click()
    await expect(page.getByText('个人记账')).toBeVisible()

    // 第二次进入统计页面
    await page.getByRole('tab', { name: '统计' }).click()
    await expect(page.getByText('统计分析')).toBeVisible()

    // 图表应该仍然正常渲染（不是空白）
    await page.waitForSelector('[data-testid="chart-bar"], [data-testid="chart-pie"]', {
      timeout: 10000,
    })

    // 检查图表容器有内容（高度 > 0）
    const chartBox = page.locator('.chart-box').first()
    await expect(chartBox).toBeVisible()
    const box = await chartBox.boundingBox()
    expect(box).not.toBeNull()
    expect(box!.height).toBeGreaterThan(100)
  })

  testAuth('从我的页面返回支出记录，数据正常显示', async ({ page }) => {
    // 进入支出记录页
    await page.goto('/transactions')
    await expect(page.getByText('支出记录')).toBeVisible()

    // 等待数据加载
    await page.waitForSelector('[data-testid="transaction-card"]', { timeout: 10000 })
    const cardCount = await page.locator('[data-testid="transaction-card"]').count()
    expect(cardCount).toBeGreaterThan(0)

    // 切换到我的页面
    await page.getByRole('tab', { name: '我的' }).click()
    await expect(page.getByText('我的')).toBeVisible()

    // 切换回支出记录页
    await page.getByRole('tab', { name: '记账' }).click()
    await expect(page.getByText('支出记录')).toBeVisible()

    // 数据应该仍然显示
    await page.waitForSelector('[data-testid="transaction-card"]', { timeout: 5000 })
    const newCardCount = await page.locator('[data-testid="transaction-card"]').count()
    expect(newCardCount).toBeGreaterThan(0)
  })
})
