import { describe, it, expect } from 'vitest'
import { centsToYuan, yuanToCents, formatAmount } from '../format'

describe('centsToYuan', () => {
  it('10050 → "100.50"', () => {
    expect(centsToYuan(10050)).toBe('100.50')
  })

  it('0 → "0.00"', () => {
    expect(centsToYuan(0)).toBe('0.00')
  })

  it('1 → "0.01"', () => {
    expect(centsToYuan(1)).toBe('0.01')
  })

  it('999 → "9.99"', () => {
    expect(centsToYuan(999)).toBe('9.99')
  })

  it('负数正常工作', () => {
    expect(centsToYuan(-500)).toBe('-5.00')
  })
})

describe('yuanToCents', () => {
  it('"100.50" → 10050', () => {
    expect(yuanToCents('100.50')).toBe(10050)
  })

  it('"0" → 0', () => {
    expect(yuanToCents('0')).toBe(0)
  })

  it('数字 100.5 → 10050', () => {
    expect(yuanToCents(100.5)).toBe(10050)
  })

  it('"abc" → 0（无效输入）', () => {
    expect(yuanToCents('abc')).toBe(0)
  })

  it('"10.555" 四舍五入 → 1056', () => {
    expect(yuanToCents('10.555')).toBe(1056)
  })
})

describe('formatAmount', () => {
  it('10050 → "¥100.50"', () => {
    expect(formatAmount(10050)).toBe('¥100.50')
  })

  it('0 → "¥0.00"', () => {
    expect(formatAmount(0)).toBe('¥0.00')
  })

  it('1 → "¥0.01"', () => {
    expect(formatAmount(1)).toBe('¥0.01')
  })
})
