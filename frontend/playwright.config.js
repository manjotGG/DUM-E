import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:8000', timezoneId: 'Asia/Kolkata', trace: 'retain-on-failure' },
  projects: [{ name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1100 } } },
    { name: 'mobile', use: { ...devices['iPhone 13'], defaultBrowserType: 'chromium' } }],
  webServer: { command: '../.venv/bin/python -m uvicorn backend.main:app --app-dir .. --host 127.0.0.1 --port 8000', url: 'http://127.0.0.1:8000/health', reuseExistingServer: !process.env.CI, timeout: 30000 },
});
