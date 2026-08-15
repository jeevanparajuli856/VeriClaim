import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { EvidenceExplorerView } from './EvidenceExplorerView';
import { mockSuccessResponse } from '../test/fixtures';
import type { EvidenceRecord } from '../api/types';

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

  it('makes duplicate evidence targets inert and renders integrity warning', () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();
    const indexWithDuplicates: EvidenceRecord[] = [
      ...mockSuccessResponse.evidence_index,
      {
        evidence_id: 'sig:DATE-001:0001', // duplicate
        kind: 'signal',
        summary: 'Duplicate signal record',
        source_refs: [],
      },
    ];

    render(
      <EvidenceExplorerView
        evidenceIndex={indexWithDuplicates}
        selectedEvidenceId="sig:DATE-001:0001"
        triggerElement={null}
        onSelectEvidence={onSelect}
        onClearSelection={onClear}
      />
    );

    // Global duplicate banner
    expect(screen.getByText(/Data Integrity Warning:/i)).toBeInTheDocument();

    // Inert duplicate target alert in detail box
    expect(screen.getByRole('heading', { name: /Duplicate Evidence Target \(Inert\)/i })).toBeInTheDocument();
    expect(screen.getByText(/Target navigation is made inert to prevent ambiguous evidence attribution/i)).toBeInTheDocument();

    // Table duplicate badges
    const duplicateBadges = screen.getAllByText(/duplicate \(inert\)/i);
    expect(duplicateBadges.length).toBe(2);
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
