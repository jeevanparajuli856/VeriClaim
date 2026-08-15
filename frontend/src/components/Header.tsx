import React from 'react';

interface HeaderProps {
  isLoading: boolean;
  hasRun: boolean;
  onRunAnalysis: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isLoading,
  hasRun,
  onRunAnalysis,
}) => {
  return (
    <header className="app-header" role="banner">
      <div className="header-container">
        <div className="header-brand">
          <h1 className="header-title">VeriClaim</h1>
          <p className="header-subtitle">
            Local Evidence-Grounded FHIR Anomaly Investigation Dashboard
          </p>
        </div>
        <div className="notice-banner" role="note" aria-label="Scope and human authority notice">

        </div>

        <div className="header-actions">
          <button
            type="button"
            id="run-analysis-button"
            className="btn btn-primary"
            onClick={onRunAnalysis}
            disabled={isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                <span>Running analysis...</span>
              </>
            ) : hasRun ? (
              <span>Run analysis again</span>
            ) : (
              <span>Run analysis</span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
