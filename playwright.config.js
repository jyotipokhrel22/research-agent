const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  use: {
    baseURL: 'http://127.0.0.1:8088',
    trace: 'on-first-retry'
  },
  webServer: {
    command: '.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8088',
    url: 'http://127.0.0.1:8088/health',
    reuseExistingServer: true,
    timeout: 30_000
  }
});
