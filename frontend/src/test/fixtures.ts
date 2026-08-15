import type {
  AnalysisResponse,
  DeterministicPipelineErrorResponse,
} from '../api/types';

export const mockSuccessResponse: AnalysisResponse = {
  analysis_id: 'demo-test-analysis-123',
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
    {
      evidence_id: 'ev:coverage:/entry/0/resource/period/start',
      source_alias: 'coverage',
      json_pointer: '/entry/0/resource/period/start',
      fact_type: 'coverage_period_start',
      value: '2015-01-01',
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
      signals: [
        {
          evidence_id: 'sig:OUTLIER-001:0001',
          rule_id: 'OUTLIER-001',
          signal_type: 'high_amount_outlier',
          priority: 'information',
          message: 'Item cost 120.0 exceeds threshold 50.0.',
          evidence_refs: ['ev:eob:/entry/0/resource/item/0/servicedDate'],
          limitations: ['Sample size is small.'],
        },
      ],
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
      evidence_id: 'ev:coverage:/entry/0/resource/period/start',
      kind: 'fact',
      summary: 'Coverage period start: 2015-01-01',
      source_refs: [],
    },
    {
      evidence_id: 'sig:DATE-001:0001',
      kind: 'signal',
      summary: 'DATE-001 signal: service date outside coverage period',
      source_refs: ['ev:eob:/entry/0/resource/item/0/servicedDate'],
    },
    {
      evidence_id: 'sig:OUTLIER-001:0001',
      kind: 'signal',
      summary: 'OUTLIER-001 signal: amount exceeds statistical threshold',
      source_refs: ['ev:eob:/entry/0/resource/item/0/servicedDate'],
    },
  ],
  gemini: {
    status: 'success',
    summary: 'Synthesized overview of 2 deterministic signals identified in the synthetic sample.',
    candidate_findings: [
      {
        title: 'Service Date Anomaly Investigation Item',
        explanation: 'The observed service date is recorded after coverage period end date.',
        evidence_refs: ['sig:DATE-001:0001', 'ev:eob:/entry/0/resource/item/0/servicedDate'],
      },
    ],
    missing_evidence: ['Missing enrollment termination reason code.'],
    limitations: ['Candidate model synthesis is non-authoritative review guidance.'],
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
    latency_ms: 1240,
    input_tokens: 850,
    output_tokens: 180,
  },
  limitations: [
    'Synthetic Blue Button 2.0 demonstration dataset only.',
    'Deterministic checks do not evaluate payer policy or clinical validity.',
  ],
};

export const mockFallbackResponse = (status: 'configuration_error' | 'timeout' | 'provider_error' | 'invalid_output' | 'invalid_evidence'): AnalysisResponse => ({
  ...mockSuccessResponse,
  gemini: {
    status,
    message: `Sanitized public message for ${status}`,
    candidate_findings: [],
    missing_evidence: [],
    limitations: ['Fallback limitation note'],
  },
  model_metadata: {
    ...mockSuccessResponse.model_metadata,
    output_validated: false,
  },
});

export const mockPipelineErrorResponse: DeterministicPipelineErrorResponse = {
  error: {
    code: 'SOURCE_UNAVAILABLE',
    message: 'Fixed synthetic JSON file was not found on local filesystem.',
    model_called: false,
  },
};
