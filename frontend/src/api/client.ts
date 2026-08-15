import { validateAnalysisResponse, validatePipelineErrorResponse } from './adapter';
import type { AnalysisState } from './types';

const ANALYZE_ENDPOINT = '/api/v1/analyze-demo';

export async function fetchAnalysis(signal?: AbortSignal): Promise<AnalysisState> {
  try {
    const response = await fetch(ANALYZE_ENDPOINT, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      signal,
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return {
        status: 'client_error',
        message: 'The local server returned a non-JSON response.',
      };
    }

    const payload: unknown = await response.json();

    if (response.status === 200) {
      const validated = validateAnalysisResponse(payload);
      if (validated) {
        return {
          status: 'success',
          data: validated,
        };
      }
      return {
        status: 'client_error',
        message: 'The analysis response did not conform to the expected schema.',
      };
    }

    if (response.status === 500) {
      const pipelineError = validatePipelineErrorResponse(payload);
      if (pipelineError) {
        return {
          status: 'pipeline_error',
          error: pipelineError,
        };
      }
      return {
        status: 'client_error',
        message: 'The pipeline error response did not match the expected schema.',
      };
    }

    return {
      status: 'client_error',
      message: `Unexpected HTTP status code: ${response.status}`,
    };
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error;
    }
    return {
      status: 'client_error',
      message: 'Failed to connect to the local analysis API at /api/v1/analyze-demo. Ensure the backend server is running.',
    };
  }
}
