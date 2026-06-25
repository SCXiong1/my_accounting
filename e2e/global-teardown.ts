import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

async function globalTeardown() {
  const storageStatePath = path.join(__dirname, 'storage-state.json')
  const metadataPath = path.join(__dirname, 'test-metadata.json')
  const testDbPath = path.join(__dirname, '..', 'backend', 'data', 'e2e-test.db')

  // 清理存储状态文件
  if (fs.existsSync(storageStatePath)) {
    fs.unlinkSync(storageStatePath)
  }

  // 清理测试元数据文件
  if (fs.existsSync(metadataPath)) {
    fs.unlinkSync(metadataPath)
  }

  // 清理测试数据库
  if (fs.existsSync(testDbPath)) {
    fs.unlinkSync(testDbPath)
  }
}

export default globalTeardown
