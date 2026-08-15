import React from 'react';

interface ClientErrorViewProps {
  message: string;
  onRetry: () => void;
  isLoading: boolean;
}

export const ClientErrorView: React.FC<ClientErrorViewProps> = ({
  message,
  onRetry,
  isLoading,
}) => {
  return (
    <section
      className="dashboard-section card client-error-card"
      aria-labelledby="client-error-heading"
      role="alert"
    >
      <div className="section-header">
        <div>
          <h2 id="client-error-heading" className="section-title text-danger">
            Connection or Transport Failure
          </h2>
          <p className="section-description">
            Could not retrieve a valid analysis result from the local service.
          </p>
        </div>
        <span className="badge badge-danger">Client Error</span>
      </div>

      <div className="error-details-box">
        <p className="error-message font-medium">{message}</p>
        <p className="text-xs text-muted mt-2">
          Verify that the local backend server is running on <code>http://127.0.0.1:8000</code> and accessible via the Vite development proxy.
        </p>
      </div>

      <div className="error-actions mt-4">
        <button
          type="button"
          className="btn btn-primary"
          onClick={onRetry}
          disabled={isLoading}
        >
          {isLoading ? 'Retrying...' : 'Retry connection'}
        </button>
      </div>
    </section>
  );
};
