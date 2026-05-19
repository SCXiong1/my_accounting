/** 格式化 Unix 秒时间戳为日期字符串 yyyy-mm-dd */
export function formatDate(ts: number): string {
  const d = new Date(ts * 1000)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** 格式化为"YY/MM/DD"短格式（含年份） */
export function formatShortDate(ts: number): string {
  const d = new Date(ts * 1000)
  const y = String(d.getFullYear()).slice(2)
  return `${y}/${d.getMonth() + 1}/${d.getDate()}`
}
