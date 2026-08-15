import type {
  AnalysisResponse,
  DeterministicPipelineError,
  GeminiResult,
} from './types';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

const VALID_GEMINI_STATUSES = new Set([
  'success',
  'configuration_error',
  'timeout',
  'provider_error',
  'invalid_output',
  'invalid_evidence',
]);

const VALID_PIPELINE_ERROR_CODES = new Set([
  'SOURCE_UNAVAILABLE',
  'SOURCE_TOO_LARGE',
  'SOURCE_INVALID_JSON',
  'SOURCE_SHAPE_UNSUPPORTED',
  'EXTRACTION_LIMIT_EXCEEDED',
]);

export function validateAnalysisResponse(data: unknown): AnalysisResponse | null {
  if (!isRecord(data)) return null;

  if (typeof data.analysis_id !== 'string' || data.analysis_id.length === 0) {
    return null;
  }

  if (!isRecord(data.source)) return null;
  if (data.source.dataset_name !== 'cms-blue-button-local-sample' || data.source.synthetic !== true) {
    return null;
  }
  if (!Array.isArray(data.source.files) || !isRecord(data.source.resource_counts)) {
    return null;
  }

  if (!Array.isArray(data.observed_facts)) return null;
  if (!Array.isArray(data.rule_results) || data.rule_results.length !== 5) return null;
  if (!Array.isArray(data.evidence_index)) return null;

  if (!isRecord(data.gemini)) return null;
  const geminiStatus = data.gemini.status;
  if (typeof geminiStatus !== 'string' || !VALID_GEMINI_STATUSES.has(geminiStatus)) {
    return null;
  }

  if (!Array.isArray(data.gemini.candidate_findings) ||
      !Array.isArray(data.gemini.missing_evidence) ||
      !Array.isArray(data.gemini.limitations)) {
    return null;
  }

  if (geminiStatus === 'success') {
    if (typeof data.gemini.summary !== 'string') return null;
  } else {
    if (typeof data.gemini.message !== 'string') return null;
  }

  if (!isRecord(data.model_metadata)) return null;
  if (!Array.isArray(data.limitations)) return null;

  return data as unknown as AnalysisResponse;
}

export function validatePipelineErrorResponse(data: unknown): DeterministicPipelineError | null {
  if (!isRecord(data)) return null;
  const error = data.error;
  if (!isRecord(error)) return null;

  if (typeof error.code !== 'string' || !VALID_PIPELINE_ERROR_CODES.has(error.code)) {
    return null;
  }
  if (typeof error.message !== 'string' || error.message.length === 0) {
    return null;
  }
  if (error.model_called !== false) {
    return null;
  }

  return error as unknown as DeterministicPipelineError;
}

export function isGeminiSuccess(gemini: GeminiResult): gemini is import('./types').GeminiSuccess {
  return gemini.status === 'success';
}

export function isGeminiFailure(gemini: GeminiResult): gemini is import('./types').GeminiFailure {
  return gemini.status !== 'success';
}
