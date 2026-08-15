import { describe, it, expect } from 'vitest';
import {
  validateAnalysisResponse,
  validatePipelineErrorResponse,
  isGeminiSuccess,
  isGeminiFailure,
} from './adapter';
import {
  mockSuccessResponse,
  mockFallbackResponse,
  mockPipelineErrorResponse,
} from '../test/fixtures';

describe('adapter', () => {
  it('validates a correct AnalysisResponse payload', () => {
    const validated = validateAnalysisResponse(mockSuccessResponse);
    expect(validated).not.toBeNull();
    expect(validated?.analysis_id).toBe('demo-test-analysis-123');
    expect(validated?.gemini.status).toBe('success');
  });

  it('validates fallback statuses', () => {
    const fallbackStatuses = [
      'configuration_error',
      'timeout',
      'provider_error',
      'invalid_output',
      'invalid_evidence',
    ] as const;

    for (const status of fallbackStatuses) {
      const resp = mockFallbackResponse(status);
      const validated = validateAnalysisResponse(resp);
      expect(validated).not.toBeNull();
      expect(validated?.gemini.status).toBe(status);
      if (validated) {
        expect(isGeminiFailure(validated.gemini)).toBe(true);
        expect(isGeminiSuccess(validated.gemini)).toBe(false);
      }
    }
  });

  it('rejects malformed payloads missing required fields', () => {
    expect(validateAnalysisResponse(null)).toBeNull();
    expect(validateAnalysisResponse('string')).toBeNull();
    expect(validateAnalysisResponse({})).toBeNull();
    expect(validateAnalysisResponse({ ...mockSuccessResponse, rule_results: [] })).toBeNull();
    expect(validateAnalysisResponse({ ...mockSuccessResponse, gemini: { status: 'unknown_status' } })).toBeNull();
  });

  it('rejects malformed nested display data', () => {
    // Nested null in source.files
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      source: { ...mockSuccessResponse.source, files: [null as unknown as typeof mockSuccessResponse.source.files[0]] },
    })).toBeNull();

    // Nested non-primitive in observed_facts value
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      observed_facts: [{ evidence_id: 'ev:eob:/x', source_alias: 'eob', json_pointer: '/x', fact_type: 't', value: {} as unknown as string }],
    })).toBeNull();

    // Non-string in evidence_refs
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      gemini: {
        ...mockSuccessResponse.gemini,
        candidate_findings: [{ title: 't', explanation: 'e', evidence_refs: [123 as unknown as string] }],
      },
    })).toBeNull();
  });

  it('strictly validates model_metadata fields', () => {
    // Valid null model when unconfigured
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      model_metadata: {
        ...mockSuccessResponse.model_metadata,
        model: null,
        latency_ms: null,
        input_tokens: null,
        output_tokens: null,
      },
    })).not.toBeNull();

    // Invalid provider
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      model_metadata: {
        ...mockSuccessResponse.model_metadata,
        provider: 'openai' as unknown as 'vertex-ai',
      },
    })).toBeNull();

    // Invalid call_count (> 1)
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      model_metadata: {
        ...mockSuccessResponse.model_metadata,
        call_count: 2,
      },
    })).toBeNull();

    // Negative tokens
    expect(validateAnalysisResponse({
      ...mockSuccessResponse,
      model_metadata: {
        ...mockSuccessResponse.model_metadata,
        input_tokens: -5,
      },
    })).toBeNull();
  });

  it('validates a correct DeterministicPipelineErrorResponse payload', () => {
    const validated = validatePipelineErrorResponse(mockPipelineErrorResponse);
    expect(validated).not.toBeNull();
    expect(validated?.code).toBe('SOURCE_UNAVAILABLE');
    expect(validated?.model_called).toBe(false);
  });

  it('rejects malformed pipeline errors', () => {
    expect(validatePipelineErrorResponse(null)).toBeNull();
    expect(validatePipelineErrorResponse({ error: { code: 'INVALID_CODE', message: 'm', model_called: false } })).toBeNull();
    expect(validatePipelineErrorResponse({ error: { code: 'SOURCE_UNAVAILABLE', message: 'm', model_called: true } })).toBeNull();
  });
});
