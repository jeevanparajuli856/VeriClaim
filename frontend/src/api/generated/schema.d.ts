export interface paths {
    "/api/v1/analyze-demo": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Analyze the fixed approved synthetic FHIR sample
         * @description Loads the three repository-owned synthetic JSON inputs, performs bounded structural extraction and five deterministic checks, and makes at most one no-tools Gemini call. The operation accepts no body, upload, path, or remote URL. Deterministic results remain available when Gemini fails.
         */
        post: operations["analyzeDemo"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        AnalysisResponse: {
            /** @description Application-generated identifier for this in-memory analysis. */
            analysis_id: string;
            source: components["schemas"]["SourceMetadata"];
            observed_facts: components["schemas"]["ObservedFact"][];
            rule_results: components["schemas"]["RuleResult"][];
            evidence_index: components["schemas"]["EvidenceRecord"][];
            gemini: components["schemas"]["GeminiSuccess"] | components["schemas"]["GeminiFailure"];
            model_metadata: components["schemas"]["ModelMetadata"];
            limitations: string[];
        };
        SourceMetadata: {
            /** @constant */
            dataset_name: "cms-blue-button-local-sample";
            /** @constant */
            synthetic: true;
            files: components["schemas"]["SourceFile"][];
            resource_counts: {
                Patient: number;
                Coverage: number;
                ExplanationOfBenefit: number;
            };
        };
        SourceFile: {
            /** @enum {string} */
            alias: "patient" | "coverage" | "eob";
            /** @enum {string} */
            path: "dataset/patient_bbuser29999.json" | "dataset/coverage_bundle_bbuser29999.json" | "dataset/eob_bundle_bbuser29999.json";
            sha256: string;
            size_bytes: number;
        };
        ObservedFact: {
            evidence_id: components["schemas"]["FactEvidenceId"];
            /** @enum {string} */
            source_alias: "patient" | "coverage" | "eob";
            json_pointer: string;
            /** @enum {string} */
            fact_type: "resource_id" | "coverage_status" | "beneficiary_reference" | "coverage_period_start" | "coverage_period_end" | "patient_reference" | "coverage_reference" | "billable_period_start" | "billable_period_end" | "service_date" | "product_service_system" | "product_service_code" | "adjudication_value" | "adjudication_currency";
            value: string | number | boolean;
        };
        RuleResult: {
            rule_id: components["schemas"]["RuleId"];
            name: string;
            /** @enum {string} */
            status: "completed" | "insufficient_evidence";
            description: string;
            formula: string;
            parameters: {
                [key: string]: string | number | boolean;
            };
            signals: components["schemas"]["DeterministicSignal"][];
            missing_evidence: string[];
            limitations: string[];
        };
        DeterministicSignal: {
            evidence_id: components["schemas"]["SignalEvidenceId"];
            rule_id: components["schemas"]["RuleId"];
            signal_type: string;
            /** @enum {string} */
            priority: "information" | "review";
            message: string;
            evidence_refs: components["schemas"]["FactEvidenceId"][];
            limitations: string[];
        };
        EvidenceRecord: {
            evidence_id: string;
            /** @enum {string} */
            kind: "fact" | "signal";
            summary: string;
            source_refs: components["schemas"]["FactEvidenceId"][];
        };
        GeminiSuccess: {
            /** @constant */
            status: "success";
            summary: string;
            candidate_findings: components["schemas"]["CandidateFinding"][];
            missing_evidence: string[];
            limitations: string[];
        };
        GeminiFailure: {
            /** @enum {string} */
            status: "configuration_error" | "timeout" | "provider_error" | "invalid_output" | "invalid_evidence";
            /** @description Sanitized public failure message; never raw provider text. */
            message: string;
            candidate_findings: unknown[];
            missing_evidence: string[];
            limitations: string[];
        };
        CandidateFinding: {
            title: string;
            explanation: string;
            evidence_refs: string[];
        };
        ModelMetadata: {
            /** @constant */
            provider: "vertex-ai";
            /** @constant */
            sdk: "google-genai";
            model: string | null;
            prompt_version: string;
            response_schema_version: string;
            invoked: boolean;
            call_count: number;
            output_validated: boolean;
            latency_ms: number | null;
            input_tokens: number | null;
            output_tokens: number | null;
        };
        DeterministicPipelineErrorResponse: {
            error: components["schemas"]["DeterministicPipelineError"];
        };
        DeterministicPipelineError: {
            /** @enum {string} */
            code: "SOURCE_UNAVAILABLE" | "SOURCE_TOO_LARGE" | "SOURCE_INVALID_JSON" | "SOURCE_SHAPE_UNSUPPORTED" | "EXTRACTION_LIMIT_EXCEEDED";
            message: string;
            /** @constant */
            model_called: false;
        };
        /** @enum {string} */
        RuleId: "REF-001" | "DATE-001" | "REPEAT-001" | "AMOUNT-001" | "OUTLIER-001";
        FactEvidenceId: string;
        SignalEvidenceId: string;
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    analyzeDemo: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Deterministic analysis completed. Inspect gemini.status to determine whether validated candidate explanations are present. */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AnalysisResponse"];
                };
            };
            /** @description The fixed source set could not be safely loaded or minimally extracted. Gemini was not called. The error is sanitized. */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DeterministicPipelineErrorResponse"];
                };
            };
        };
    };
}
