import React, { useState, useMemo, useEffect, useRef } from 'react';
import type { EvidenceRecord } from '../api/types';

interface EvidenceExplorerViewProps {
  evidenceIndex: EvidenceRecord[];
  selectedEvidenceId: string | null;
  triggerElement: HTMLElement | null;
  onSelectEvidence: (evidenceId: string, triggerElement: HTMLElement | null) => void;
  onClearSelection: () => void;
}

export const EvidenceExplorerView: React.FC<EvidenceExplorerViewProps> = ({
  evidenceIndex,
  selectedEvidenceId,
  triggerElement,
  onSelectEvidence,
  onClearSelection,
}) => {
  const [filterText, setFilterText] = useState('');
  const selectedHeadingRef = useRef<HTMLHeadingElement | null>(null);

  // Build map and detect duplicates
  const { evidenceMap, duplicateIds } = useMemo(() => {
    const counts = new Map<string, number>();
    evidenceIndex.forEach((rec) => {
      counts.set(rec.evidence_id, (counts.get(rec.evidence_id) || 0) + 1);
    });

    const dupes = new Set<string>();
    const map = new Map<string, { record: EvidenceRecord; index: number }>();

    evidenceIndex.forEach((rec, idx) => {
      if ((counts.get(rec.evidence_id) || 0) > 1) {
        dupes.add(rec.evidence_id);
      } else {
        map.set(rec.evidence_id, { record: rec, index: idx });
      }
    });

    return { evidenceMap: map, duplicateIds: Array.from(dupes) };
  }, [evidenceIndex]);

  const isDuplicateSelected = Boolean(selectedEvidenceId && duplicateIds.includes(selectedEvidenceId));
  const selectedItem = selectedEvidenceId && !isDuplicateSelected ? evidenceMap.get(selectedEvidenceId) : null;
  const isSelectedMissing = Boolean(selectedEvidenceId && !isDuplicateSelected && !selectedItem);

  // When selectedEvidenceId changes, focus and scroll into view
  useEffect(() => {
    if (selectedEvidenceId && selectedHeadingRef.current) {
      selectedHeadingRef.current.focus();
    }
  }, [selectedEvidenceId]);

  const handleReturnFocus = () => {
    onClearSelection();
    if (triggerElement && document.body.contains(triggerElement)) {
      triggerElement.focus();
    }
  };

  const filteredList = useMemo(() => {
    if (!filterText) return evidenceIndex;
    const term = filterText.toLowerCase();
    return evidenceIndex.filter(
      (e) =>
        e.evidence_id.toLowerCase().includes(term) ||
        e.summary.toLowerCase().includes(term) ||
        e.kind.toLowerCase().includes(term)
    );
  }, [evidenceIndex, filterText]);

  return (
    <section
      id="evidence-explorer"
      className="dashboard-section card"
      aria-labelledby="evidence-explorer-heading"
    >
      <div className="section-header">
        <div>
          <h2 id="evidence-explorer-heading" className="section-title">
            Evidence Explorer
          </h2>
          <p className="section-description">
            Complete response-local index of facts and signals with stable identifiers ({evidenceIndex.length} records).
          </p>
        </div>

        {selectedEvidenceId && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleReturnFocus}
            title="Return focus to invoking control"
          >
            ← Return to trigger
          </button>
        )}
      </div>

      {/* Duplicate ID integrity warning */}
      {duplicateIds.length > 0 && (
        <div className="status-alert alert-warning" role="alert">
          <strong>Data Integrity Warning:</strong> Duplicate evidence IDs detected in response index:
          <ul className="text-xs mt-1">
            {duplicateIds.map((id) => (
              <li key={id}><code>{id}</code> (rendered inert to prevent ambiguous resolution)</li>
            ))}
          </ul>
        </div>
      )}

      {/* Selected Evidence Highlight / Detail Box */}
      {selectedEvidenceId && (
        <div
          className="selected-evidence-card"
          id="selected-evidence-focus-target"
        >
          {isDuplicateSelected ? (
            <div className="status-alert alert-warning" role="alert">
              <h3
                ref={selectedHeadingRef}
                tabIndex={-1}
                className="alert-title outline-none"
              >
                Duplicate Evidence Target (Inert)
              </h3>
              <p className="text-sm">
                Referenced identifier <code>{selectedEvidenceId}</code> occurs multiple times in the response index and cannot resolve unambiguously. Target navigation is made inert to prevent ambiguous evidence attribution.
              </p>
            </div>
          ) : isSelectedMissing ? (
            <div className="status-alert alert-danger" role="alert">
              <h3
                ref={selectedHeadingRef}
                tabIndex={-1}
                className="alert-title outline-none"
              >
                Evidence Target Not Found
              </h3>
              <p className="text-sm">
                Referenced identifier <code>{selectedEvidenceId}</code> is not present in the current response evidence index.
              </p>
            </div>
          ) : selectedItem ? (
            <div className="evidence-detail-box">
              <div className="detail-header">
                <h3
                  ref={selectedHeadingRef}
                  tabIndex={-1}
                  className="detail-title font-mono outline-none"
                >
                  {selectedItem.record.evidence_id}
                </h3>
                <span
                  className={`badge ${
                    selectedItem.record.kind === 'signal'
                      ? 'badge-alert'
                      : 'badge-info'
                  }`}
                >
                  Kind: {selectedItem.record.kind}
                </span>
              </div>

              <p className="detail-summary font-semibold">
                {selectedItem.record.summary}
              </p>

              {selectedItem.record.source_refs && selectedItem.record.source_refs.length > 0 && (
                <div className="detail-source-refs">
                  <span className="text-xs text-muted font-semibold">
                    Underlying Source References:
                  </span>
                  <div className="refs-chips">
                    {selectedItem.record.source_refs.map((ref) => (
                      <button
                        key={ref}
                        type="button"
                        className="chip-ref"
                        onClick={(e) => onSelectEvidence(ref, e.currentTarget)}
                        title={`View referenced fact: ${ref}`}
                      >
                        {ref}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}

      {/* Filter / Search bar */}
      <div className="filter-bar">
        <label htmlFor="evidence-search-input" className="filter-label">
          Search evidence records:
        </label>
        <input
          id="evidence-search-input"
          type="search"
          className="input-text"
          placeholder="Filter by evidence ID, kind, or summary..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
        />
        {filterText && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setFilterText('')}
          >
            Clear
          </button>
        )}
      </div>

      {/* Evidence index list / table */}
      <div className="table-container" tabIndex={0} role="region" aria-label="Evidence index table">
        <table className="data-table">
          <thead>
            <tr>
              <th scope="col">Safe Index</th>
              <th scope="col">Evidence ID</th>
              <th scope="col">Kind</th>
              <th scope="col">Summary</th>
              <th scope="col">Source References</th>
            </tr>
          </thead>
          <tbody>
            {filteredList.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-4 text-muted">
                  No evidence records match the search filter.
                </td>
              </tr>
            ) : (
              filteredList.map((rec, index) => {
                const isCurrent = selectedEvidenceId === rec.evidence_id;
                const isDupe = duplicateIds.includes(rec.evidence_id);
                return (
                  <tr
                    key={`${rec.evidence_id}-${index}`}
                    id={`evidence-row-${index}`}
                    className={isCurrent ? 'row-selected' : undefined}
                  >
                    <td className="font-mono text-xs text-muted">#{index + 1}</td>
                    <td>
                      <button
                        type="button"
                        className="btn-link font-mono text-xs"
                        onClick={(e) => onSelectEvidence(rec.evidence_id, e.currentTarget)}
                        title={`Select evidence: ${rec.evidence_id}`}
                      >
                        {rec.evidence_id}
                      </button>
                      {isDupe && (
                        <span className="badge badge-warning text-xs ml-1" title="Duplicate ID in evidence index">
                          duplicate (inert)
                        </span>
                      )}
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          rec.kind === 'signal' ? 'badge-alert' : 'badge-neutral'
                        }`}
                      >
                        {rec.kind}
                      </span>
                    </td>
                    <td>{rec.summary}</td>
                    <td>
                      {rec.source_refs && rec.source_refs.length > 0 ? (
                        <div className="refs-chips">
                          {rec.source_refs.map((ref) => (
                            <button
                              key={ref}
                              type="button"
                              className="chip-ref text-xs"
                              onClick={(e) => onSelectEvidence(ref, e.currentTarget)}
                            >
                              {ref}
                            </button>
                          ))}
                        </div>
                      ) : (
                        <span className="text-muted text-xs">—</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
};
