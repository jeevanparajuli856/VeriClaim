import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="app-footer" role="contentinfo">
      <div className="footer-container">
        <p className="footer-text">
          <strong>VeriClaim</strong> — Local Evidence-Grounded FHIR Anomaly Investigation Prototype.
        </p>
        <p className="footer-disclaimer text-xs text-muted">
          All data processed is local, synthetic demonstration data. This system does not access, store, or process
          Protected Health Information (PHI) and makes no claim of HIPAA compliance, healthcare diagnostic validity,
          or clinical decision-making.
        </p>
      </div>
    </footer>
  );
};
