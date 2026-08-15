import React from 'react';

interface LimitationsViewProps {
  limitations: string[];
}

export const LimitationsView: React.FC<LimitationsViewProps> = ({ limitations }) => {
  if (!limitations || limitations.length === 0) return null;

  return (
    <section className="dashboard-section card" aria-labelledby="limitations-heading">
      <div className="section-header">
        <h2 id="limitations-heading" className="section-title">
          System & Demonstration Limitations
        </h2>
        <span className="badge badge-neutral">{limitations.length} Items</span>
      </div>

      <ul className="limitations-list">
        {limitations.map((lim, idx) => (
          <li key={idx} className="limitation-item">
            {lim}
          </li>
        ))}
      </ul>
    </section>
  );
};
