# 01: 提取 withMutate 错误处理包装函数

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 1 — 地基
**Dependencies:** 无

## Summary

在 `lib/feedback.ts` 中添加 `withMutate` 包装函数，替代所有视图中 ~15 处重复的 try-catch 模式。

## Interface

```typescript
async function withMutate(
  fn: () => Promise<void>,
  successMsg: string,
  fallbackMsg: string
): Promise<void>
```

## Acceptance Criteria

- [ ] `withMutate` 函数实现：调用 fn()，成功时 `showSuccess(successMsg)`，失败时 `showError(getErrorMessage(e, fallbackMsg))`
- [ ] 所有视图中的 try-catch 模式替换为 `withMutate` 调用
- [ ] `npm run build` 通过

## Files

- `frontend/src/lib/feedback.ts` — 新增 `withMutate`
- 所有 View 文件 — 替换 try-catch 样板

## Test Strategy

无独立测试。`npm run build` 类型检查即可——这是一个纯组合函数，不对已有行为做变更。

## Comments

