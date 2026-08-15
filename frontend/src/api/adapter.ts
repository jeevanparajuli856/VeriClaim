import type {
  AnalysisResponse,
  DeterministicPipelineError,
  GeminiResult,
  RuleId,
} from './types';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

const VALID_GEMINI_STATUSES = new Set([
  'success',
  'configuration_error',
  'timeout',
  'provider_error',
  'invalid_output',
  'invalid_evidence',
]);

const VALID_RULE_IDS = new Set<RuleId>([
  'REF-001',
  'DATE-001',
  'REPEAT-001',
  'AMOUNT-001',
  'OUTLIER-001',
]);

const VALID_SOURCE_ALIASES = new Set(['patient', 'coverage', 'eob']);

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

  // Validate source
  if (!isRecord(data.source)) return null;
  if (data.source.dataset_name !== 'cms-blue-button-local-sample' || data.source.synthetic !== true) {
    return null;
  }
  if (!Array.isArray(data.source.files) || data.source.files.length !== 3) {
    return null;
  }
  for (const file of data.source.files) {
    if (!isRecord(file)) return null;
    if (typeof file.alias !== 'string' || !VALID_SOURCE_ALIASES.has(file.alias)) return null;
    if (typeof file.path !== 'string' || file.path.length === 0) return null;
    if (typeof file.sha256 !== 'string' || file.sha256.length === 0) return null;
    if (typeof file.size_bytes !== 'number' || file.size_bytes <= 0) return null;
  }

  if (!isRecord(data.source.resource_counts)) return null;
  if (
    typeof data.source.resource_counts.Patient !== 'number' ||
    typeof data.source.resource_counts.Coverage !== 'number' ||
    typeof data.source.resource_counts.ExplanationOfBenefit !== 'number'
  ) {
    return null;
  }

  // Validate observed facts
  if (!Array.isArray(data.observed_facts)) return null;
  for (const fact of data.observed_facts) {
    if (!isRecord(fact)) return null;
    if (typeof fact.evidence_id !== 'string' || fact.evidence_id.length === 0) return null;
    if (typeof fact.source_alias !== 'string' || !VALID_SOURCE_ALIASES.has(fact.source_alias)) return null;
    if (typeof fact.json_pointer !== 'string' || !fact.json_pointer.startsWith('/')) return null;
    if (typeof fact.fact_type !== 'string' || fact.fact_type.length === 0) return null;
    if (
      typeof fact.value !== 'string' &&
      typeof fact.value !== 'number' &&
      typeof fact.value !== 'boolean'
    ) {
      return null;
    }
  }

  // Validate rule results
  if (!Array.isArray(data.rule_results) || data.rule_results.length !== 5) return null;
  for (const rule of data.rule_results) {
    if (!isRecord(rule)) return null;
    if (typeof rule.rule_id !== 'string' || !VALID_RULE_IDS.has(rule.rule_id as RuleId)) return null;
    if (typeof rule.name !== 'string' || rule.name.length === 0) return null;
    if (rule.status !== 'completed' && rule.status !== 'insufficient_evidence') return null;
    if (typeof rule.description !== 'string' || typeof rule.formula !== 'string') return null;
    if (!isRecord(rule.parameters)) return null;
    for (const val of Object.values(rule.parameters)) {
      if (typeof val !== 'string' && typeof val !== 'number' && typeof val !== 'boolean') {
        return null;
      }
    }
    if (!Array.isArray(rule.signals)) return null;
    for (const sig of rule.signals) {
      if (!isRecord(sig)) return null;
      if (typeof sig.evidence_id !== 'string' || !sig.evidence_id.startsWith('sig:')) return null;
      if (typeof sig.rule_id !== 'string' || !VALID_RULE_IDS.has(sig.rule_id as RuleId)) return null;
      if (typeof sig.signal_type !== 'string' || sig.signal_type.length === 0) return null;
      if (sig.priority !== 'information' && sig.priority !== 'review') return null;
      if (typeof sig.message !== 'string' || sig.message.length === 0) return null;
      if (!isStringArray(sig.evidence_refs)) return null;
      if (!isStringArray(sig.limitations)) return null;
    }
    if (!isStringArray(rule.missing_evidence)) return null;
    if (!isStringArray(rule.limitations)) return null;
  }

  // Validate evidence index
  if (!Array.isArray(data.evidence_index)) return null;
  for (const item of data.evidence_index) {
    if (!isRecord(item)) return null;
    if (typeof item.evidence_id !== 'string' || item.evidence_id.length === 0) return null;
    if (item.kind !== 'fact' && item.kind !== 'signal') return null;
    if (typeof item.summary !== 'string' || item.summary.length === 0) return null;
    if (!isStringArray(item.source_refs)) return null;
  }

  // Validate Gemini block
  if (!isRecord(data.gemini)) return null;
  const geminiStatus = data.gemini.status;
  if (typeof geminiStatus !== 'string' || !VALID_GEMINI_STATUSES.has(geminiStatus)) {
    return null;
  }

  if (!Array.isArray(data.gemini.candidate_findings) ||
      !isStringArray(data.gemini.missing_evidence) ||
      !isStringArray(data.gemini.limitations)) {
    return null;
  }

  if (geminiStatus === 'success') {
    if (typeof data.gemini.summary !== 'string' || data.gemini.summary.length === 0) return null;
    for (const finding of data.gemini.candidate_findings) {
      if (!isRecord(finding)) return null;
      if (typeof finding.title !== 'string' || finding.title.length === 0) return null;
      if (typeof finding.explanation !== 'string' || finding.explanation.length === 0) return null;
      if (!isStringArray(finding.evidence_refs)) return null;
    }
  } else {
    if (typeof data.gemini.message !== 'string' || data.gemini.message.length === 0) return null;
  }

  // Validate model metadata
  if (!isRecord(data.model_metadata)) return null;
  const meta = data.model_metadata;
  if (meta.provider !== 'vertex-ai' || meta.sdk !== 'google-genai') {
    return null;
  }
  if (meta.model !== null && (typeof meta.model !== 'string' || meta.model.length === 0 || meta.model.length > 160)) {
    return null;
  }
  if (typeof meta.prompt_version !== 'string' || meta.prompt_version.length === 0 || meta.prompt_version.length > 64) {
    return null;
  }
  if (
    typeof meta.response_schema_version !== 'string' ||
    meta.response_schema_version.length === 0 ||
    meta.response_schema_version.length > 64
  ) {
    return null;
  }
  if (typeof meta.invoked !== 'boolean') {
    return null;
  }
  if (
    typeof meta.call_count !== 'number' ||
    !Number.isInteger(meta.call_count) ||
    (meta.call_count !== 0 && meta.call_count !== 1)
  ) {
    return null;
  }
  if (typeof meta.output_validated !== 'boolean') {
    return null;
  }
  if (
    meta.latency_ms !== null &&
    (typeof meta.latency_ms !== 'number' || !Number.isInteger(meta.latency_ms) || meta.latency_ms < 0)
  ) {
    return null;
  }
  if (
    meta.input_tokens !== null &&
    (typeof meta.input_tokens !== 'number' || !Number.isInteger(meta.input_tokens) || meta.input_tokens < 0)
  ) {
    return null;
  }
  if (
    meta.output_tokens !== null &&
    (typeof meta.output_tokens !== 'number' || !Number.isInteger(meta.output_tokens) || meta.output_tokens < 0)
  ) {
    return null;
  }

  // Validate limitations
  if (!isStringArray(data.limitations) || data.limitations.length === 0) return null;

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
