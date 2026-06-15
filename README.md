# EzExpense

轻量级移动端个人记账 Web 应用。手机浏览器即可记录支出、分类管理、标签筛选、统计分析。

## 功能特性

- 快速记账 — 金额、分类、标签、备注、时间，一键提交
- 分类标签联动 — 选择分类后自动过滤历史关联标签，筛选更精准
- 自定义分类与标签 — 注册即预设 8 个常用分类，支持增删改和拖拽排序
- 关键词搜索 — 按备注、金额、分类、标签全文检索
- 多维统计 — 按分类/标签饼图、按月趋势柱状图，支持灵活时间范围筛选
- 时间筛选 — 支出记录页支持本月/近3月/近6月/今年/自定义时间范围
- 回收站 — 软删除一键恢复，支持批量选择永久删除
- PWA — 添加到手机主屏幕，独立窗口显示
- 多用户 — JWT 认证，数据按用户隔离

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.12 / FastAPI / SQLAlchemy 2.0 (async) / SQLite / Alembic |
| 前端 | Vue 3 / TypeScript / Vite / Vant 4 / Pinia / ECharts |
| 认证 | JWT (HS256) + bcrypt |
| 部署 | Docker 多阶段构建 / GHCR |

## 快速开始

### Docker 部署（推荐）

```bash
docker compose up -d
```

手机浏览器访问 `http://<服务器IP>:8080`。

### 拉取镜像

```bash
docker pull ghcr.io/scxiong1/my_accounting:2.0.0
```

### 本地开发

**后端：**

```bash
cd backend
uv venv
uv pip install -r requirements.txt
.venv/bin/python main.py
```

**前端：**

```bash
cd frontend
npm ci
npm run dev
```

开发环境访问 `http://localhost:5173`，生产构建访问 `http://localhost:8080`。

## 项目结构

```
backend/
  api/                # FastAPI 路由处理
  services/           # 业务逻辑
  models/             # SQLAlchemy ORM 模型
  schemas/            # Pydantic 请求/响应模型
  middleware/          # JWT 认证 + 全局异常处理
frontend/
  src/
    views/            # 页面组件
    stores/           # Pinia 状态管理
    components/       # 共享 UI 组件
    composables/      # Vue 组合式函数（图表、筛选）
    lib/              # HTTP 客户端、Token 管理、消息通知
    core/             # 纯工具函数（格式化、时间）
    styles/           # 设计令牌 (tokens.css) + 全局样式覆盖 (global.css)
e2e/
  tests/              # 12 个 E2E 测试：S1 认证、S2 支出 CRUD、S3 表单交互、S4 统计、S5 下拉刷新、S6 分类管理、S7 标签管理、S8 导航稳定性、S9 表单优化、S10 分类标签联动、S11 列表筛选、S12 回收站批量删除
```

## 开发指南

### 运行测试

```bash
# 后端单元测试
cd backend
.venv/bin/python -m pytest test_catalog_core.py test_soft_delete.py test_statistics.py -v

# 后端集成测试（需要启动服务器）
.venv/bin/python -m pytest test_api.py test_linkage.py test_batch_delete.py -v

# 前端测试
cd frontend
npx vitest

# E2E 测试（首次需要安装浏览器）
cd e2e
npm ci
npx playwright install --with-deps chromium webkit
npm test
```

### 数据库迁移

```bash
cd backend
.venv/bin/python -m alembic upgrade head                    # 执行迁移
.venv/bin/python -m alembic revision --autogenerate -m "描述"  # 创建迁移
```

## 配置

后端配置文件 `backend/config.yaml`，支持环境变量覆盖：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `APP_SERVER_PORT` | 服务端口 | `8080` |
| `APP_DATABASE_PATH` | 数据库路径 | `./data/ezexpense.db` |
| `APP_SECURITY_JWT_SECRET` | JWT 签名密钥 | 配置文件中的值 |

## 部署

生产构建由 FastAPI 直接托管前端静态文件。CI 在推送 `v*` 标签时自动构建并发布 Docker 镜像到 GHCR。

```bash
git tag v2.0.0
git push origin v2.0.0
```

镜像标签说明：
- `2.0.0` — 精确版本，推荐生产使用
- `2.0` — 次级版本，跟随补丁更新
- `latest` — 始终指向最新版本

## 许可证

私有项目。
