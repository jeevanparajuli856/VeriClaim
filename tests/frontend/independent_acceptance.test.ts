import { afterEach, describe, expect, it, vi } from 'vitest';

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
});
