import os

# 测试数据库隔离 — 必须在服务器启动时设置此环境变量：
#   APP_DATABASE_PATH=./data/test.db uvicorn main:app --host 0.0.0.0 --port 8080
os.environ.setdefault("APP_DATABASE_PATH", "./data/test.db")

BASE = "http://localhost:8080"
