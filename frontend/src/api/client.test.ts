import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchAnalysis } from './client';
import {
  mockSuccessResponse,
  mockPipelineErrorResponse,
} from '../test/fixtures';

describe('client', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('handles successful HTTP 200 response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => mockSuccessResponse,
    });

    const result = await fetchAnalysis();
    expect(result.status).toBe('success');
    if (result.status === 'success') {
      expect(result.data.analysis_id).toBe('demo-test-analysis-123');
    }
  });

  it('handles HTTP 500 deterministic pipeline error', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 500,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => mockPipelineErrorResponse,
    });

    const result = await fetchAnalysis();
    expect(result.status).toBe('pipeline_error');
    if (result.status === 'pipeline_error') {
      expect(result.error.code).toBe('SOURCE_UNAVAILABLE');
    }
  });

  it('handles non-JSON response as client_error', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      status: 200,
      headers: new Headers({ 'content-type': 'text/html' }),
      text: async () => '<html>Error</html>',
    });

    const result = await fetchAnalysis();
    expect(result.status).toBe('client_error');
  });

  it('handles network error as client_error', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network offline'));

    const result = await fetchAnalysis();
    expect(result.status).toBe('client_error');
    if (result.status === 'client_error') {
      expect(result.message).toContain('Failed to connect');
    }
  });

  it('propagates AbortError when aborted', async () => {
    const abortErr = new DOMException('Aborted', 'AbortError');
    globalThis.fetch = vi.fn().mockRejectedValue(abortErr);

    await expect(fetchAnalysis()).rejects.toThrow('Aborted');
  });
});
