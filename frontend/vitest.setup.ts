// jsdom provides localStorage natively — no mock needed
import { afterEach } from 'vitest'

// Cleanup after each test
afterEach(() => {
  localStorage.clear()
})
