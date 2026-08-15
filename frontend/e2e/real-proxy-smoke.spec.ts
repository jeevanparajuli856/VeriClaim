import { test, expect } from '@playwright/test';

test.describe('Real FastAPI Backend + Vite Proxy Browser Smoke', () => {
  test('executes genuine credential-free analysis through /api proxy', async ({ page }) => {
    // Navigate directly without route interception
    await page.goto('/');

    await expect(page.getByRole('heading', { level: 1 })).toHaveText('VeriClaim');
    await expect(page.getByRole('heading', { name: 'Ready to Investigate' })).toBeVisible();

    // Trigger analysis
    const runBtn = page.getByRole('button', { name: 'Run analysis' });
    await runBtn.click();

    // Verify deterministic rule checks render from real backend execution
    await expect(page.getByRole('heading', { name: 'Deterministic Rule Checks' })).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#rule-section-REF-001')).toBeVisible();
    await expect(page.locator('#rule-section-DATE-001')).toBeVisible();
    await expect(page.locator('#rule-section-REPEAT-001')).toBeVisible();
    await expect(page.locator('#rule-section-AMOUNT-001')).toBeVisible();
    await expect(page.locator('#rule-section-OUTLIER-001')).toBeVisible();

    // Verify source dataset metadata
    await expect(page.getByText('cms-blue-button-local-sample')).toBeVisible();

    // In credential-free environment, Vertex AI fallback is safely rendered
    await expect(page.getByText(/Deterministic-Only Mode/i)).toBeVisible();
  });
});
