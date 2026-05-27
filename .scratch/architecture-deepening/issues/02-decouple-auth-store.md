# 02: 解耦 auth store 与 Vue Router

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 1 — 地基
**Dependencies:** 无（独立于 01）

## Summary

从 `stores/auth.ts` 移除 `useRouter()`，`logout()` 只清除状态和 token。导航逻辑移到 `App.vue`。

## Acceptance Criteria

- [ ] `stores/auth.ts` 不再 import `vue-router`
- [ ] `logout()` 只做：清除 token、清除 user、调用 `router.push('/login')` 的逻辑移除
- [ ] `App.vue` watch token 变化，token 为 null 时自动 `router.push('/login')`
- [ ] `npm run build` 通过
- [ ] 手动验证：登录 → 退出登录 → 正确跳转到 /login

## Files

- `frontend/src/stores/auth.ts` — 移除 router 依赖
- `frontend/src/App.vue` — 添加 token watch 导航

## Test Strategy

无独立测试。手动验证退出登录流程。

## Comments

