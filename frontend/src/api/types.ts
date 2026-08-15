import type { components } from './generated/schema';

export type AnalysisResponse = components['schemas']['AnalysisResponse'];
export type SourceMetadata = components['schemas']['SourceMetadata'];
export type SourceFile = components['schemas']['SourceFile'];
export type ObservedFact = components['schemas']['ObservedFact'];
export type RuleResult = components['schemas']['RuleResult'];
export type DeterministicSignal = components['schemas']['DeterministicSignal'];
export type EvidenceRecord = components['schemas']['EvidenceRecord'];
export type GeminiSuccess = components['schemas']['GeminiSuccess'];
export type GeminiFailure = components['schemas']['GeminiFailure'];
export type GeminiResult = GeminiSuccess | GeminiFailure;
export type CandidateFinding = components['schemas']['CandidateFinding'];
export type ModelMetadata = components['schemas']['ModelMetadata'];
export type DeterministicPipelineErrorResponse = components['schemas']['DeterministicPipelineErrorResponse'];
export type DeterministicPipelineError = components['schemas']['DeterministicPipelineError'];
export type RuleId = components['schemas']['RuleId'];
export type FactEvidenceId = components['schemas']['FactEvidenceId'];
export type SignalEvidenceId = components['schemas']['SignalEvidenceId'];

export type AnalysisState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: AnalysisResponse }
  | { status: 'pipeline_error'; error: DeterministicPipelineError }
  | { status: 'client_error'; message: string };
