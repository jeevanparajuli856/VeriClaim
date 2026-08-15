import React, { useState } from 'react';
import type { ObservedFact } from '../api/types';

interface ObservedFactsViewProps {
  facts: ObservedFact[];
  onSelectEvidence: (evidenceId: string, triggerElement: HTMLElement | null) => void;
}

export const ObservedFactsView: React.FC<ObservedFactsViewProps> = ({
  facts,
  onSelectEvidence,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filterText, setFilterText] = useState('');

  const filteredFacts = facts.filter((f) => {
    if (!filterText) return true;
    const term = filterText.toLowerCase();
    return (
      f.evidence_id.toLowerCase().includes(term) ||
      f.fact_type.toLowerCase().includes(term) ||
      f.source_alias.toLowerCase().includes(term) ||
      String(f.value).toLowerCase().includes(term)
    );
  });

  return (
    <section className="dashboard-section card" aria-labelledby="observed-facts-heading">
      <div className="section-header">
        <div>
          <h2 id="observed-facts-heading" className="section-title">
            Observed Facts
          </h2>
          <p className="section-description">
            Structured, RFC 6901-pointer indexed facts extracted deterministically from supported FHIR resources ({facts.length} total).
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          aria-controls="observed-facts-content"
        >
          {isExpanded ? 'Collapse facts' : 'View all facts'}
        </button>
      </div>

      {isExpanded && (
        <div id="observed-facts-content" className="collapsible-content">
          <div className="filter-bar">
            <label htmlFor="facts-search-input" className="filter-label">
              Filter facts:
            </label>
            <input
              id="facts-search-input"
              type="search"
              className="input-text"
              placeholder="Search by evidence ID, type, source, or value..."
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

          <div className="table-container" tabIndex={0} role="region" aria-label="Observed facts data table">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">Evidence ID</th>
                  <th scope="col">Source</th>
                  <th scope="col">Fact Type</th>
                  <th scope="col">Pointer</th>
                  <th scope="col">Extracted Value</th>
                </tr>
              </thead>
              <tbody>
                {filteredFacts.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-muted">
                      No facts matching filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredFacts.map((fact) => (
                    <tr key={fact.evidence_id}>
                      <td>
                        <button
                          type="button"
                          className="btn-link font-mono text-xs"
                          onClick={(e) => onSelectEvidence(fact.evidence_id, e.currentTarget)}
                          title={`View in Evidence Explorer: ${fact.evidence_id}`}
                        >
                          {fact.evidence_id}
                        </button>
                      </td>
                      <td>
                        <span className="badge badge-neutral">{fact.source_alias}</span>
                      </td>
                      <td>
                        <code>{fact.fact_type}</code>
                      </td>
                      <td className="font-mono text-xs text-muted">{fact.json_pointer}</td>
                      <td className="font-mono">{String(fact.value)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
};
