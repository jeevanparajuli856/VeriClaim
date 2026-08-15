import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const mockSuccessData = {
  analysis_id: 'demo-e2e-analysis-456',
  source: {
    dataset_name: 'cms-blue-button-local-sample',
    synthetic: true,
    files: [
      {
        alias: 'patient',
        path: 'dataset/patient_bbuser29999.json',
        sha256: 'a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90',
        size_bytes: 6196,
      },
      {
        alias: 'coverage',
        path: 'dataset/coverage_bundle_bbuser29999.json',
        sha256: 'b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1',
        size_bytes: 12450,
      },
      {
        alias: 'eob',
        path: 'dataset/eob_bundle_bbuser29999.json',
        sha256: 'c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2',
        size_bytes: 45800,
      },
    ],
    resource_counts: {
      Patient: 1,
      Coverage: 4,
      ExplanationOfBenefit: 10,
    },
  },
  observed_facts: [
    {
      evidence_id: 'ev:patient:/id',
      source_alias: 'patient',
      json_pointer: '/id',
      fact_type: 'resource_id',
      value: 'bbuser29999',
    },
    {
      evidence_id: 'ev:eob:/entry/0/resource/item/0/servicedDate',
      source_alias: 'eob',
      json_pointer: '/entry/0/resource/item/0/servicedDate',
      fact_type: 'service_date',
      value: '2015-10-01',
    },
  ],
  rule_results: [
    {
      rule_id: 'REF-001',
      name: 'Reference Resolution Check',
      status: 'completed',
      description: 'Verifies Patient and Coverage references.',
      formula: 'referenced_id in loaded_resources',
      parameters: { strict: true },
      signals: [],
      missing_evidence: [],
      limitations: ['Only checks internal sample references.'],
    },
    {
      rule_id: 'DATE-001',
      name: 'Coverage Service Date Window Check',
      status: 'completed',
      description: 'Compares service dates with coverage period bounds.',
      formula: 'coverage_start <= service_date <= coverage_end',
      parameters: { grace_days: 0 },
      signals: [
        {
          evidence_id: 'sig:DATE-001:0001',
          rule_id: 'DATE-001',
          signal_type: 'service_outside_coverage',
          priority: 'review',
          message: 'Service date 2015-10-01 is outside coverage period.',
          evidence_refs: ['ev:eob:/entry/0/resource/item/0/servicedDate'],
          limitations: ['Does not evaluate retro-enrollment policies.'],
        },
      ],
      missing_evidence: [],
      limitations: ['Requires exact date fields.'],
    },
    {
      rule_id: 'REPEAT-001',
      name: 'Exact Duplicate Service Signature Check',
      status: 'completed',
      description: 'Checks for duplicate claim items.',
      formula: 'count(item_signature) > 1',
      parameters: { match_mode: 'exact' },
      signals: [],
      missing_evidence: [],
      limitations: ['Exact match only.'],
    },
    {
      rule_id: 'AMOUNT-001',
      name: 'Adjudication Balance Check',
      status: 'completed',
      description: 'Verifies sum of patient paid and benefit equal total drug cost.',
      formula: 'abs(drugcost - (benefit + paidbypatient)) <= 0.01',
      parameters: { tolerance: 0.01 },
      signals: [],
      missing_evidence: [],
      limitations: ['Single-currency items only.'],
    },
    {
      rule_id: 'OUTLIER-001',
      name: 'Tukey Hinges Outlier Check',
      status: 'completed',
      description: 'Identifies amounts exceeding Q3 + 1.5 * IQR threshold.',
      formula: 'drugcost > Q3 + 1.5 * IQR',
      parameters: { threshold: 50 },
      signals: [],
      missing_evidence: [],
      limitations: ['Requires minimum 4 observations.'],
    },
  ],
  evidence_index: [
    {
      evidence_id: 'ev:patient:/id',
      kind: 'fact',
      summary: 'Patient resource ID: bbuser29999',
      source_refs: [],
    },
    {
      evidence_id: 'ev:eob:/entry/0/resource/item/0/servicedDate',
      kind: 'fact',
      summary: 'Service date for EOB item: 2015-10-01',
      source_refs: [],
    },
    {
      evidence_id: 'sig:DATE-001:0001',
      kind: 'signal',
      summary: 'DATE-001 signal: service date outside coverage period',
      source_refs: ['ev:eob:/entry/0/resource/item/0/servicedDate'],
    },
  ],
  gemini: {
    status: 'success',
    summary: 'Bounded candidate synthesis for synthetic Blue Button sample.',
    candidate_findings: [
      {
        title: 'Coverage Period Discrepancy',
        explanation: 'The service date occurs after the recorded coverage end date.',
        evidence_refs: ['sig:DATE-001:0001'],
      },
    ],
    missing_evidence: [],
    limitations: ['Model synthesis is non-authoritative review guidance.'],
  },
  model_metadata: {
    provider: 'vertex-ai',
    sdk: 'google-genai',
    model: 'gemini-1.5-pro',
    prompt_version: 'v1.0.0',
    response_schema_version: 'v1.0.0',
    invoked: true,
    call_count: 1,
    output_validated: true,
    latency_ms: 1100,
    input_tokens: 800,
    output_tokens: 150,
  },
  limitations: ['Local synthetic demonstration sample only.'],
};

test.describe('VeriClaim Dashboard E2E', () => {
  test('renders initial idle view and executes analysis flow', async ({ page }) => {
    await page.route('**/api/v1/analyze-demo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSuccessData),
      });
    });

    await page.goto('/');

    // Check title and landmarks
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('VeriClaim');
    await expect(page.getByRole('banner')).toBeVisible();
    await expect(page.getByRole('main')).toBeVisible();
    await expect(page.getByRole('contentinfo')).toBeVisible();

    // Check idle state
    await expect(page.getByRole('heading', { name: 'Ready to Investigate' })).toBeVisible();

    // Run analysis
    const runBtn = page.getByRole('button', { name: 'Run analysis' });
    await runBtn.click();

    // Verify results render
    await expect(page.getByRole('heading', { name: 'Source & Sample Metadata' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Deterministic Rule Checks' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Candidate Gemini Summary & Findings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Evidence Explorer' })).toBeVisible();

    // Verify all 5 rules are displayed
    await expect(page.locator('#rule-section-REF-001')).toBeVisible();
    await expect(page.locator('#rule-section-DATE-001')).toBeVisible();
    await expect(page.locator('#rule-section-REPEAT-001')).toBeVisible();
    await expect(page.locator('#rule-section-AMOUNT-001')).toBeVisible();
    await expect(page.locator('#rule-section-OUTLIER-001')).toBeVisible();

    // Verify responsive layout has no horizontal overflow
    const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(hasOverflow).toBe(false);

    // Run accessibility check on completed results
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('evidence reference navigation and focus return flow', async ({ page }) => {
    await page.route('**/api/v1/analyze-demo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSuccessData),
      });
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Run analysis' }).click();

    await expect(page.getByRole('heading', { name: 'Deterministic Rule Checks' })).toBeVisible();

    // Click evidence reference chip in Candidate Finding
    const chipRef = page.locator('.findings-grid').getByRole('button', { name: 'sig:DATE-001:0001' });
    await chipRef.click();

    // Verify Evidence Explorer is visible and return button is available
    const returnBtn = page.getByRole('button', { name: '← Return to trigger' });
    await expect(returnBtn).toBeVisible();

    // Click return button to restore focus
    await returnBtn.click();
    await expect(chipRef).toBeFocused();
  });

  test('handles duplicate evidence IDs by rendering inert targets and integrity warning', async ({ page }) => {
    const dataWithDuplicates = {
      ...mockSuccessData,
      evidence_index: [
        ...mockSuccessData.evidence_index,
        {
          evidence_id: 'sig:DATE-001:0001', // duplicate
          kind: 'signal',
          summary: 'Duplicate signal record',
          source_refs: [],
        },
      ],
    };

    await page.route('**/api/v1/analyze-demo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(dataWithDuplicates),
      });
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Run analysis' }).click();

    await expect(page.getByText(/Data Integrity Warning: Duplicate evidence IDs detected/i)).toBeVisible();

    // Click duplicate reference chip
    const chipRef = page.locator('.findings-grid').getByRole('button', { name: 'sig:DATE-001:0001' });
    await chipRef.click();

    // Verify inert duplicate target alert is displayed and focused
    await expect(page.getByRole('heading', { name: 'Duplicate Evidence Target (Inert)' })).toBeVisible();
    await expect(page.getByText(/Target navigation is made inert to prevent ambiguous evidence attribution/i)).toBeVisible();
  });

  test('handles typed fallback state when Gemini fails validation', async ({ page }) => {
    const fallbackData = {
      ...mockSuccessData,
      gemini: {
        status: 'configuration_error',
        message: 'Google Cloud Vertex AI credentials not configured in local environment.',
        candidate_findings: [],
        missing_evidence: [],
        limitations: ['Fallback limitation'],
      },
      model_metadata: {
        ...mockSuccessData.model_metadata,
        output_validated: false,
      },
    };

    await page.route('**/api/v1/analyze-demo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(fallbackData),
      });
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Run analysis' }).click();

    await expect(page.getByText(/Deterministic-Only Mode \(configuration_error\)/i)).toBeVisible();
    await expect(page.getByText(/Google Cloud Vertex AI credentials not configured/i)).toBeVisible();

    // Verify deterministic rule results are fully retained
    await expect(page.locator('#rule-section-DATE-001')).toBeVisible();
  });

  test('handles deterministic pipeline failure (HTTP 500) and allows retry', async ({ page }) => {
    let callCount = 0;
    await page.route('**/api/v1/analyze-demo', async (route) => {
      callCount++;
      if (callCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            error: {
              code: 'SOURCE_UNAVAILABLE',
              message: 'Local dataset files could not be located.',
              model_called: false,
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSuccessData),
        });
      }
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Run analysis' }).click();

    await expect(page.getByRole('heading', { name: 'Deterministic Pipeline Extraction Failure' })).toBeVisible();
    await expect(page.getByText(/model_called: false/i)).toBeVisible();

    // Click retry
    await page.getByRole('button', { name: 'Retry analysis' }).click();

    // Now success should be shown
    await expect(page.getByRole('heading', { name: 'Source & Sample Metadata' })).toBeVisible();
  });

  test('supports reduced-motion preference without layout breakages', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.route('**/api/v1/analyze-demo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSuccessData),
      });
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Run analysis' }).click();

    await expect(page.getByRole('heading', { name: 'Deterministic Rule Checks' })).toBeVisible();
    const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(hasOverflow).toBe(false);
  });
});
