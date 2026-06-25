import { describe, it, expect } from 'vitest'
import { formatDate, formatShortDate } from '../time'

describe('formatDate', () => {
  it('返回 YYYY-MM-DD 格式', () => {
    // 2024-01-15 00:00:00 UTC = 1705276800
    expect(formatDate(1705276800)).toBe('2024-01-15')
  })

  it('处理 0 时间戳（1970-01-01）', () => {
    expect(formatDate(0)).toBe('1970-01-01')
  })

  it('月份和日期补零', () => {
    // 2024-03-05 00:00:00 UTC = 1709596800
    expect(formatDate(1709596800)).toBe('2024-03-05')
  })
})

describe('formatShortDate', () => {
  it('返回 YY/M/D 格式（不补零）', () => {
    // 2024-01-15 00:00:00 UTC = 1705276800
    expect(formatShortDate(1705276800)).toBe('24/1/15')
  })

  it('处理 0 时间戳', () => {
    expect(formatShortDate(0)).toBe('70/1/1')
  })
})
