import React from 'react';
import type { AnalysisState } from '../api/types';

interface StatusLiveRegionProps {
  state: AnalysisState;
}

export const StatusLiveRegion: React.FC<StatusLiveRegionProps> = ({ state }) => {
  let message = '';

  switch (state.status) {
    case 'idle':
      message = 'Ready to analyze local dataset.';
      break;
    case 'loading':
      message = 'Running investigation analysis on synthetic sample...';
      break;
    case 'success':
      if (state.data.gemini.status === 'success') {
        message = 'Analysis complete. Deterministic signals and Gemini candidate findings ready.';
      } else {
        message = `Analysis complete with deterministic rules. Gemini fallback: ${state.data.gemini.status}.`;
      }
      break;
    case 'pipeline_error':
      message = `Deterministic pipeline error: ${state.error.code}. ${state.error.message}`;
      break;
    case 'client_error':
      message = `Connection error: ${state.message}`;
      break;
  }

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
      role="status"
    >
      {message}
    </div>
  );
};
