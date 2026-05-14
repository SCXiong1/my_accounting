/**
 * 金额格式化工具
 * API 传输用「分」（整数），前端展示用「元」（字符串）
 */

/** 分 → 元（保留两位小数） */
export function centsToYuan(cents: number): string {
  return (cents / 100).toFixed(2)
}

/** 元 → 分（输入字符串转为整数） */
export function yuanToCents(yuan: string | number): number {
  const num = typeof yuan === 'string' ? parseFloat(yuan) : yuan
  if (isNaN(num)) return 0
  return Math.round(num * 100)
}

/** 格式化金额为展示用字符串：¥12.50 */
export function formatAmount(cents: number): string {
  return `¥${centsToYuan(cents)}`
}
