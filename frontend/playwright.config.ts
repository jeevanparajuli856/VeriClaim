import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chromium',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: [
    {
      command: 'python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000',
      url: 'http://127.0.0.1:8000/docs',
      cwd: '..',
      reuseExistingServer: false,
      env: {
        GOOGLE_CLOUD_PROJECT: '',
        GOOGLE_CLOUD_LOCATION: '',
        VERTEX_GEMINI_MODEL: '',
        GOOGLE_GENAI_USE_VERTEXAI: '0',
      },
      timeout: 30000,
    },
    {
      command: 'npm run dev',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 30000,
    },
  ],
});
