import { test as base, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface TestMetadata {
  user: { id: number; username: string; nickname: string };
  token: string;
  tags: { id: number; name: string }[];
  expenses: { id: number; amount: number; note: string; category_id: number; tag_ids: number[] }[];
}

export function loadMetadata(): TestMetadata {
  const metadataPath = path.join(__dirname, '..', 'test-metadata.json');
  if (!fs.existsSync(metadataPath)) {
    throw new Error('test-metadata.json 不存在，请先运行 global-setup');
  }
  return JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
}

export const testNoAuth = base.extend<{}>({
  context: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: { cookies: [], origins: [] } });
    await use(context);
    await context.close();
  },
  page: async ({ context }, use) => {
    const page = await context.newPage();
    await use(page);
  },
});

export { expect };
