import React from 'react';
import type { GeminiResult, ModelMetadata } from '../api/types';
import { isGeminiSuccess } from '../api/adapter';

interface GeminiSummaryViewProps {
  gemini: GeminiResult;
  modelMetadata: ModelMetadata;
  onSelectEvidence: (evidenceId: string, triggerElement: HTMLElement | null) => void;
}

export const GeminiSummaryView: React.FC<GeminiSummaryViewProps> = ({
  gemini,
  modelMetadata,
  onSelectEvidence,
}) => {
  const isSuccess = isGeminiSuccess(gemini);

  return (
    <section className="dashboard-section card gemini-section" aria-labelledby="gemini-findings-heading">
      <div className="section-header">
        <div>
          <div className="flex items-center gap-2">
            <h2 id="gemini-findings-heading" className="section-title">
              Candidate Gemini Summary & Findings
            </h2>
            <span className="badge badge-non-authoritative">
              Non-Authoritative Candidate Aid
            </span>
          </div>
          <p className="section-description">
            Bounded synthesis from Vertex AI Gemini based strictly on supplied synthetic facts and signals.
            Model findings do not establish fraud, coverage, coding correctness, medical necessity, or clinical diagnosis.
          </p>
        </div>

        <div>
          <span
            className={`badge ${
              isSuccess ? 'badge-success' : 'badge-warning'
            }`}
          >
            Status: {gemini.status}
          </span>
        </div>
      </div>

      {/* Model status alert for fallback states */}
      {!isSuccess && (
        <div className="status-alert alert-warning" role="alert">
          <h3 className="alert-title font-semibold">
            Deterministic-Only Mode ({gemini.status})
          </h3>
          <p className="alert-message">{gemini.message}</p>
          <p className="text-xs mt-1 text-muted">
            All deterministic signals and observed facts remain fully available and authoritative above.
          </p>
        </div>
      )}

      {/* Model success output */}
      {isSuccess && (
        <div className="gemini-success-content">
          <div className="gemini-summary-box">
            <h3 className="subsection-title">Candidate Synthesis</h3>
            <p className="gemini-summary-text">{gemini.summary}</p>
          </div>

          <div className="candidate-findings-section">
            <h3 className="subsection-title">
              Candidate Findings ({gemini.candidate_findings.length})
            </h3>
            {gemini.candidate_findings.length === 0 ? (
              <p className="text-muted text-sm">No candidate findings were highlighted by the model.</p>
            ) : (
              <div className="findings-grid">
                {gemini.candidate_findings.map((finding, idx) => (
                  <div key={idx} className="finding-card">
                    <h4 className="finding-title">{finding.title}</h4>
                    <p className="finding-explanation">{finding.explanation}</p>
                    <div className="finding-evidence-refs">
                      <span className="text-xs text-muted font-semibold">Cited Evidence:</span>
                      <div className="refs-chips">
                        {finding.evidence_refs.map((ref) => (
                          <button
                            key={ref}
                            type="button"
                            className="chip-ref"
                            onClick={(e) => onSelectEvidence(ref, e.currentTarget)}
                            title={`Jump to evidence: ${ref}`}
                          >
                            {ref}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Missing evidence & limitations */}
      <div className="gemini-meta-notes">
        {gemini.missing_evidence.length > 0 && (
          <div className="meta-note-box">
            <h4 className="text-xs font-semibold text-warning">
              Gemini Identified Missing Evidence ({gemini.missing_evidence.length})
            </h4>
            <ul className="text-xs text-muted mt-1">
              {gemini.missing_evidence.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {gemini.limitations.length > 0 && (
          <div className="meta-note-box">
            <h4 className="text-xs font-semibold text-muted">
              Model Limitations ({gemini.limitations.length})
            </h4>
            <ul className="text-xs text-muted mt-1">
              {gemini.limitations.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Model Metadata */}
      <div className="model-metadata-section">
        <details className="text-xs">
          <summary className="cursor-pointer font-semibold text-muted">
            Model & Invocation Metadata ({modelMetadata.provider}/{modelMetadata.sdk})
          </summary>
          <div className="metadata-grid mt-2">
            <div className="meta-item">
              <span className="meta-label">Provider:</span>
              <span className="meta-value">{modelMetadata.provider}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">SDK:</span>
              <span className="meta-value">{modelMetadata.sdk}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Model:</span>
              <span className="meta-value font-mono">{modelMetadata.model ?? 'None'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Prompt Version:</span>
              <span className="meta-value font-mono">{modelMetadata.prompt_version}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Invoked:</span>
              <span className="meta-value">{modelMetadata.invoked ? 'Yes' : 'No'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Call Count:</span>
              <span className="meta-value">{modelMetadata.call_count}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Output Validated:</span>
              <span className="meta-value">{modelMetadata.output_validated ? 'Yes' : 'No'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Latency:</span>
              <span className="meta-value">
                {modelMetadata.latency_ms !== null ? `${modelMetadata.latency_ms} ms` : 'N/A'}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Tokens:</span>
              <span className="meta-value">
                In: {modelMetadata.input_tokens ?? 'N/A'} | Out: {modelMetadata.output_tokens ?? 'N/A'}
              </span>
            </div>
          </div>
        </details>
      </div>
    </section>
  );
};
