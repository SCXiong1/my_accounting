# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

移动端个人支出记账 Web 应用，部署在服务器/NAS 上，手机浏览器访问（PWA 可添加到桌面）。用户和老婆两人使用，各自独立账号。只做支出记录和统计分析，不搞复杂功能。

## 技术栈

| 层 | 选型 |
|----|------|
| 后端语言 | Python 3.12+ |
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0 + Alembic（数据库迁移） |
| 数据库 | SQLite 3（零配置，数据即文件） |
| 认证 | JWT（python-jose）+ bcrypt |
| 前端框架 | 待定（Vue 3 / React），纯移动端 PWA |
| 图表库 | ECharts |
| 构建工具 | Vite |
| 部署 | Docker 或 uvicorn 直接运行 |

## 项目结构

```
backend/
  main.py                      # 应用入口
  config.py                    # 配置管理（YAML + 环境变量覆盖）
  database.py                  # 数据库连接 + 会话管理
  models/                      # SQLAlchemy ORM 模型
    user.py / expense_category.py / expense_tag.py
    expense.py / expense_tag_index.py
  schemas/                     # Pydantic 请求/响应模型
  api/                         # API 路由（Handler）
    __init__.py / auth.py / users.py / categories.py
    tags.py / expenses.py / statistics.py
  services/                    # 业务逻辑层
  middleware/                   # JWT 认证 + 异常处理
  utils/security.py            # JWT 生成/验证、密码哈希

frontend/
  src/
    main.ts / App.vue (或 App.tsx)
    stores/                    # 状态管理
    views/                     # 页面（Login, Home, ExpenseList, ExpenseForm,
                               #   CategoryManage, TagManage, Statistics, Profile）
    components/                # 通用组件
    core/                      # 纯业务逻辑（金额格式化、日期处理）
    lib/                       # 基础设施（API 客户端、Token 管理）
    router/                    # 路由定义

data/                          # 运行时数据（ezexpense.db）
config.yaml                    # 配置文件
```

## 后端分层架构

```
HTTP 请求
  → FastAPI Router（api/__init__.py）
  → Middleware（CORS → JWT 认证 → 全局异常处理）
  → API Handler（api/*.py：Pydantic 参数校验、调用 Service）
  → Service（services/*.py：业务逻辑、事务管理）
  → SQLAlchemy Session（数据访问、查询）
  → SQLite
```

分层规则：
- API 层：只做参数校验和调用 Service，不写业务逻辑
- Service 层：包含所有业务规则（创建支出时维护标签关联、删除分类时检查是否有支出），管理事务
- Models 层：SQLAlchemy ORM 模型定义
- Schemas 层：Pydantic 请求/响应模型

## 数据模型（5 张表）

- **user**：id, username, password(bcrypt), nickname, created_at, updated_at
- **expense_category**：id, uid, name, icon, color, display_order, deleted, 时间戳
- **expense_tag**：id, uid, name, display_order, deleted, 时间戳
- **expense**：id, uid, amount(分), category_id, transaction_time, timezone_offset, note, deleted, 时间戳
- **expense_tag_index**：id, uid, expense_id, tag_id, created_at（多对多关联）

## 关键设计规则

1. **金额用整数（分）**：`100.50 元 → 10050`，永远不用浮点数
2. **时间戳用 Unix 秒**：所有时间字段为整数 Unix timestamp
3. **软删除**：expense、category、tag 表用 `deleted` + `deleted_at`，查询始终加 `deleted = 0`
4. **用户隔离**：所有数据表带 `uid`，所有查询加 `uid = ?`
5. **标签多对多**：通过 expense_tag_index 关联，支出创建/修改时原子性维护
6. **配置环境变量覆盖**：`APP_SERVER_PORT=9090` 覆盖 `config.yaml` 中的 `server.port`

## API 约定

- Base URL：`/api/v1`（需认证）或 `/api`（认证接口）
- 认证：JWT，Header `Authorization: Bearer <token>`
- 成功：直接返回 JSON 数据
- 错误：`{"detail": "错误描述"}`（FastAPI 默认格式）
- 分页：游标分页，`cursor` + `limit`（默认 20）

## 核心 API 一览

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | POST `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh` | 注册（自动创建预设分类）/登录/刷新令牌 |
| 用户 | GET/PUT `/api/v1/user/profile` | 个人信息 |
| 分类 | GET/POST `/api/v1/categories`, PUT/DELETE `/:id`, PUT `/sort` | CRUD + 排序，有支出的分类不可删除 |
| 标签 | GET/POST `/api/v1/tags`, PUT/DELETE `/:id`, PUT `/sort` | CRUD + 排序 |
| 支出 | GET/POST `/api/v1/expenses`, GET/PUT/DELETE `/:id` | 列表支持游标分页 + 时间/分类/标签/关键词筛选 |
| 统计 | GET `/api/v1/statistics/overview` | 今日/本周/本月/今年总额 |
| 统计 | GET `/api/v1/statistics/by_category` | 按分类统计，支持时间范围 + 标签筛选 |
| 统计 | GET `/api/v1/statistics/by_tag` | 按标签统计，支持时间范围 + 分类筛选 |
| 统计 | GET `/api/v1/statistics/monthly` | 月度趋势，支持分类 + 标签筛选 |

## 事务管理

Service 层关键操作使用 `async with db.begin()` 管理事务：
- 创建/修改支出 + 标签关联维护
- 删除标签 + 清除关联
- 用户注册 + 预设分类创建

## 开发路线图

- **Phase 1（核心骨架）**：项目结构、5 张表模型、注册/登录、分类/标签/支出 CRUD
- **Phase 2（前端可用）**：前端框架搭建、登录/注册页、首页概览、支出列表/表单、分类/标签管理
- **Phase 3（统计完善）**：4 个统计接口 + ECharts 图表（饼图/柱状图），交叉筛选
- **Phase 4（体验打磨）**：CSV 导出、PWA 离线、搜索优化、预算提醒

## 详细规格文档

完整的数据库 DDL、API 接口规范（含请求/响应示例）、统计 SQL 示例、前端页面路由等细节见 `项目说明书.md`。
