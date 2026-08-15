import React, { useState, useRef, useEffect, useCallback } from 'react';
import type { AnalysisState } from './api/types';
import { fetchAnalysis } from './api/client';
import { SkipLink } from './components/SkipLink';
import { Header } from './components/Header';
import { StatusLiveRegion } from './components/StatusLiveRegion';
import { SourceMetadataView } from './components/SourceMetadataView';
import { ObservedFactsView } from './components/ObservedFactsView';
import { RuleResultsView } from './components/RuleResultsView';
import { GeminiSummaryView } from './components/GeminiSummaryView';
import { EvidenceExplorerView } from './components/EvidenceExplorerView';
import { LimitationsView } from './components/LimitationsView';
import { PipelineErrorView } from './components/PipelineErrorView';
import { ClientErrorView } from './components/ClientErrorView';
import { Footer } from './components/Footer';

export const App: React.FC = () => {
  const [state, setState] = useState<AnalysisState>({ status: 'idle' });
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [triggerElement, setTriggerElement] = useState<HTMLElement | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const runAnalysis = useCallback(async () => {
    if (state.status === 'loading') {
      return; // Prevent concurrent requests
    }

    // Abort existing in-flight request if any
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Reset previous selection and transition to loading
    setSelectedEvidenceId(null);
    setTriggerElement(null);
    setState({ status: 'loading' });

    try {
      const result = await fetchAnalysis(controller.signal);
      setState(result);
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // Request was deliberately aborted; ignore
        return;
      }
      setState({
        status: 'client_error',
        message: 'An unexpected client-side error occurred during analysis.',
      });
    }
  }, [state.status]);

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleSelectEvidence = useCallback((evidenceId: string, trigger: HTMLElement | null) => {
    setSelectedEvidenceId(evidenceId);
    if (trigger) {
      setTriggerElement(trigger);
    }

    // Scroll evidence explorer into view respecting user motion preference
    const explorerEl = document.getElementById('evidence-explorer');
    if (explorerEl) {
      const prefersReducedMotion =
        typeof window !== 'undefined' &&
        typeof window.matchMedia === 'function' &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      explorerEl.scrollIntoView({
        behavior: prefersReducedMotion ? 'auto' : 'smooth',
        block: 'start',
      });
    }
  }, []);

  const handleClearSelection = useCallback(() => {
    setSelectedEvidenceId(null);
  }, []);

  const isLoading = state.status === 'loading';
  const hasRun = state.status !== 'idle';

  return (
    <div className="app-layout">
      <SkipLink />
      <StatusLiveRegion state={state} />

      <Header
        isLoading={isLoading}
        hasRun={hasRun}
        onRunAnalysis={runAnalysis}
      />

      <main id="main-content" className="main-content" role="main">
        {state.status === 'idle' && (
          <section className="idle-hero card" aria-labelledby="idle-welcome-heading">
            <h2 id="idle-welcome-heading" className="text-xl font-bold text-slate-900">
              Ready to Investigate
            </h2>
            <p className="text-muted mt-2">
              Select <strong>Run analysis</strong> above to perform deterministic FHIR invariant checks and
              synthesize structured findings on the fixed synthetic Blue Button sample dataset.
            </p>
            <div className="idle-features-grid mt-4">
              <div className="idle-feature-item">
                <span className="font-semibold block">5 Deterministic Rules</span>
                <span className="text-xs text-muted">
                  Reference resolution, Coverage dates, Duplicate items, Amount balances, and Outliers.
                </span>
              </div>
              <div className="idle-feature-item">
                <span className="font-semibold block">Evidence-Grounded Citations</span>
                <span className="text-xs text-muted">
                  Every signal and candidate finding maps directly to stable, RFC 6901-indexed evidence.
                </span>
              </div>
              <div className="idle-feature-item">
                <span className="font-semibold block">Transparent Model Fallback</span>
                <span className="text-xs text-muted">
                  Vertex AI candidate synthesis fails gracefully without discarding deterministic rule reports.
                </span>
              </div>
            </div>
          </section>
        )}

        {state.status === 'loading' && (
          <section className="loading-state card" aria-busy="true" aria-label="Loading analysis">
            <div className="loading-spinner-container">
              <div className="spinner spinner-large" aria-hidden="true" />
              <p className="loading-title font-semibold mt-4">
                Executing Deterministic Invariant Checks & Structured Model Synthesis...
              </p>
              <p className="text-xs text-muted mt-1">
                Loading local synthetic Patient, Coverage, and ExplanationOfBenefit resources.
              </p>
            </div>
          </section>
        )}

        {state.status === 'pipeline_error' && (
          <PipelineErrorView
            error={state.error}
            onRetry={runAnalysis}
            isLoading={isLoading}
          />
        )}

        {state.status === 'client_error' && (
          <ClientErrorView
            message={state.message}
            onRetry={runAnalysis}
            isLoading={isLoading}
          />
        )}

        {state.status === 'success' && (
          <div className="analysis-results-view">
            <SourceMetadataView
              source={state.data.source}
              analysisId={state.data.analysis_id}
            />

            <ObservedFactsView
              facts={state.data.observed_facts}
              onSelectEvidence={handleSelectEvidence}
            />

            <RuleResultsView
              ruleResults={state.data.rule_results}
              onSelectEvidence={handleSelectEvidence}
            />

            <GeminiSummaryView
              gemini={state.data.gemini}
              modelMetadata={state.data.model_metadata}
              onSelectEvidence={handleSelectEvidence}
            />

            <EvidenceExplorerView
              evidenceIndex={state.data.evidence_index}
              selectedEvidenceId={selectedEvidenceId}
              triggerElement={triggerElement}
              onSelectEvidence={handleSelectEvidence}
              onClearSelection={handleClearSelection}
            />

            <LimitationsView limitations={state.data.limitations} />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default App;
