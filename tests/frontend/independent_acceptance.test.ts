import { afterEach, describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';

import {
  validateAnalysisResponse,
  validatePipelineErrorResponse,
} from '../../frontend/src/api/adapter';
import { fetchAnalysis } from '../../frontend/src/api/client';
import {
  mockFallbackResponse,
  mockSuccessResponse,
} from '../../frontend/src/test/fixtures';

const PIPELINE_CODES = [
  'SOURCE_UNAVAILABLE',
  'SOURCE_TOO_LARGE',
  'SOURCE_INVALID_JSON',
  'SOURCE_SHAPE_UNSUPPORTED',
  'EXTRACTION_LIMIT_EXCEEDED',
] as const;

const GEMINI_FALLBACK_STATUSES = [
  'configuration_error',
  'timeout',
  'provider_error',
  'invalid_output',
  'invalid_evidence',
] as const;

describe('FRONTEND-001 independent acceptance boundaries', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it.each(GEMINI_FALLBACK_STATUSES)(
    'accepts the typed %s fallback without discarding deterministic results',
    (status) => {
      const response = mockFallbackResponse(status);
      const validated = validateAnalysisResponse(response);

      expect(validated?.gemini.status).toBe(status);
      expect(validated?.rule_results).toHaveLength(5);
      expect(validated?.evidence_index.length).toBeGreaterThan(0);
    },
  );

  it.each(PIPELINE_CODES)('accepts the typed %s pipeline failure', (code) => {
    expect(
      validatePipelineErrorResponse({
        error: {
          code,
          message: 'Sanitized public pipeline failure.',
          model_called: false,
        },
      }),
    ).toEqual({
      code,
      message: 'Sanitized public pipeline failure.',
      model_called: false,
    });
  });

  it('uses only the relative bodyless POST operation', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => mockSuccessResponse,
    });

    await fetchAnalysis();

    expect(globalThis.fetch).toHaveBeenCalledOnce();
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/v1/analyze-demo',
      expect.objectContaining({ method: 'POST' }),
    );
    const request = vi.mocked(globalThis.fetch).mock.calls[0]?.[1];
    expect(request).not.toHaveProperty('body');
    expect(request).not.toHaveProperty('credentials');
  });

  it('rejects malformed nested display data at the network boundary', () => {
    const malformed = {
      ...mockSuccessResponse,
      source: {
        ...mockSuccessResponse.source,
        files: [null],
      },
    };

    expect(validateAnalysisResponse(malformed)).toBeNull();
  });

  it('rejects malformed model metadata at the network boundary', () => {
    for (const modelMetadata of [
      null,
      { ...mockSuccessResponse.model_metadata, provider: 'unexpected-provider' },
      { ...mockSuccessResponse.model_metadata, call_count: 2 },
      { ...mockSuccessResponse.model_metadata, invoked: 'yes' },
      { ...mockSuccessResponse.model_metadata, latency_ms: -1 },
      { ...mockSuccessResponse.model_metadata, input_tokens: 1.5 },
    ]) {
      expect(validateAnalysisResponse({
        ...mockSuccessResponse,
        model_metadata: modelMetadata,
      })).toBeNull();
    }
  });

  it('keeps Vite local-only and Playwright free of host-library mutation', () => {
    const viteConfig = readFileSync(
      new URL('../../frontend/vite.config.ts', import.meta.url),
      'utf8',
    );
    const playwrightConfig = readFileSync(
      new URL('../../frontend/playwright.config.ts', import.meta.url),
      'utf8',
    );

    expect(viteConfig).toContain("host: '127.0.0.1'");
    expect(viteConfig).toContain("target: 'http://127.0.0.1:8000'");
    expect(viteConfig).not.toMatch(/server\s*:\s*\{[\s\S]*?fs\s*:/);
    expect(playwrightConfig).toContain('reuseExistingServer: false');
    expect(playwrightConfig).not.toContain('LD_LIBRARY_PATH');
    expect(playwrightConfig).not.toMatch(/\/home\/[A-Za-z0-9._-]+/);
  });

  it('aligns the runtime engine and Node type surface to Node 24', () => {
    const packageJson = JSON.parse(readFileSync(
      new URL('../../frontend/package.json', import.meta.url),
      'utf8',
    )) as {
      engines?: { node?: string };
      devDependencies?: Record<string, string>;
    };

    expect(packageJson.engines?.node).toMatch(/^\^24\./);
    expect(packageJson.devDependencies?.['@types/node']).toMatch(/^\^24\./);
  });
});
