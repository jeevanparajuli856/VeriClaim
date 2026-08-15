import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { EvidenceExplorerView } from './EvidenceExplorerView';
import { mockSuccessResponse } from '../test/fixtures';

describe('EvidenceExplorerView', () => {
  it('renders all evidence records in index table', () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();
    render(
      <EvidenceExplorerView
        evidenceIndex={mockSuccessResponse.evidence_index}
        selectedEvidenceId={null}
        triggerElement={null}
        onSelectEvidence={onSelect}
        onClearSelection={onClear}
      />
    );

    expect(screen.getByRole('heading', { level: 2, name: /Evidence Explorer/i })).toBeInTheDocument();
    expect(screen.getByText('ev:patient:/id')).toBeInTheDocument();
    expect(screen.getByText('sig:DATE-001:0001')).toBeInTheDocument();
  });

  it('renders selected evidence card with detail and return button', () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();
    const triggerBtn = document.createElement('button');
    document.body.appendChild(triggerBtn);
    const focusSpy = vi.spyOn(triggerBtn, 'focus');

    render(
      <EvidenceExplorerView
        evidenceIndex={mockSuccessResponse.evidence_index}
        selectedEvidenceId="sig:DATE-001:0001"
        triggerElement={triggerBtn}
        onSelectEvidence={onSelect}
        onClearSelection={onClear}
      />
    );

    const summaries = screen.getAllByText(/DATE-001 signal: service date outside coverage period/i);
    expect(summaries.length).toBeGreaterThan(0);

    const returnBtn = screen.getByRole('button', { name: /Return to trigger/i });
    expect(returnBtn).toBeInTheDocument();

    fireEvent.click(returnBtn);
    expect(onClear).toHaveBeenCalled();
    expect(focusSpy).toHaveBeenCalled();

    document.body.removeChild(triggerBtn);
  });

  it('renders data integrity warning for missing evidence reference', () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();
    render(
      <EvidenceExplorerView
        evidenceIndex={mockSuccessResponse.evidence_index}
        selectedEvidenceId="ev:nonexistent:/item"
        triggerElement={null}
        onSelectEvidence={onSelect}
        onClearSelection={onClear}
      />
    );

    expect(screen.getByText(/Evidence Target Not Found/i)).toBeInTheDocument();
    expect(screen.getByText(/ev:nonexistent:\/item/i)).toBeInTheDocument();
  });

  it('filters evidence records with search input', () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();
    render(
      <EvidenceExplorerView
        evidenceIndex={mockSuccessResponse.evidence_index}
        selectedEvidenceId={null}
        triggerElement={null}
        onSelectEvidence={onSelect}
        onClearSelection={onClear}
      />
    );

    const searchInput = screen.getByLabelText(/Search evidence records:/i);
    fireEvent.change(searchInput, { target: { value: 'patient' } });

    expect(screen.getByText('ev:patient:/id')).toBeInTheDocument();
    expect(screen.queryByText('sig:DATE-001:0001')).not.toBeInTheDocument();
  });
});
