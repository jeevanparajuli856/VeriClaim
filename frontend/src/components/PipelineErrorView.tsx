import React from 'react';
import type { DeterministicPipelineError } from '../api/types';

interface PipelineErrorViewProps {
  error: DeterministicPipelineError;
  onRetry: () => void;
  isLoading: boolean;
}

export const PipelineErrorView: React.FC<PipelineErrorViewProps> = ({
  error,
  onRetry,
  isLoading,
}) => {
  return (
    <section
      className="dashboard-section card pipeline-error-card"
      aria-labelledby="pipeline-error-heading"
      role="alert"
    >
      <div className="section-header">
        <div>
          <h2 id="pipeline-error-heading" className="section-title text-danger">
            Deterministic Pipeline Extraction Failure
          </h2>
          <p className="section-description">
            The fixed local source dataset could not be safely loaded or extracted by the backend pipeline.
          </p>
        </div>
        <span className="badge badge-danger">Code: {error.code}</span>
      </div>

      <div className="error-details-box">
        <p className="error-message font-medium">{error.message}</p>
        <p className="text-xs text-muted mt-2">
          <strong>Boundary Note:</strong> Vertex AI Gemini was not invoked (<code>model_called: false</code>). No partial analysis was fabricated.
        </p>
      </div>

      <div className="error-actions mt-4">
        <button
          type="button"
          className="btn btn-primary"
          onClick={onRetry}
          disabled={isLoading}
        >
          {isLoading ? 'Retrying analysis...' : 'Retry analysis'}
        </button>
      </div>
    </section>
  );
};
