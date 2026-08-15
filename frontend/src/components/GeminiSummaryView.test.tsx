import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GeminiSummaryView } from './GeminiSummaryView';
import { mockSuccessResponse, mockFallbackResponse } from '../test/fixtures';

describe('GeminiSummaryView', () => {
  it('renders success state with candidate findings and non-authoritative label', () => {
    const onSelect = vi.fn();
    render(
      <GeminiSummaryView
        gemini={mockSuccessResponse.gemini}
        modelMetadata={mockSuccessResponse.model_metadata}
        onSelectEvidence={onSelect}
      />
    );

    expect(screen.getByText(/Non-Authoritative Candidate Aid/i)).toBeInTheDocument();
    expect(screen.getByText(/Synthesized overview of 2 deterministic signals/i)).toBeInTheDocument();
    expect(screen.getByText(/Service Date Anomaly Investigation Item/i)).toBeInTheDocument();

    const chip = screen.getByRole('button', { name: 'sig:DATE-001:0001' });
    fireEvent.click(chip);
    expect(onSelect).toHaveBeenCalledWith('sig:DATE-001:0001', expect.anything());
  });

  it('renders fallback states with alert banner and sanitized message', () => {
    const onSelect = vi.fn();
    const fallbackData = mockFallbackResponse('configuration_error');
    render(
      <GeminiSummaryView
        gemini={fallbackData.gemini}
        modelMetadata={fallbackData.model_metadata}
        onSelectEvidence={onSelect}
      />
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Deterministic-Only Mode \(configuration_error\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Sanitized public message for configuration_error/i)).toBeInTheDocument();
  });
});
