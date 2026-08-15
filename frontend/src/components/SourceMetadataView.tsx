import React from 'react';
import type { SourceMetadata } from '../api/types';

interface SourceMetadataViewProps {
  source: SourceMetadata;
  analysisId: string;
}

export const SourceMetadataView: React.FC<SourceMetadataViewProps> = ({
  source,
  analysisId,
}) => {
  return (
    <section className="dashboard-section card" aria-labelledby="source-metadata-heading">
      <div className="section-header">
        <h2 id="source-metadata-heading" className="section-title">
          Source & Sample Metadata
        </h2>
        <span className="badge badge-info">Synthetic Sample</span>
      </div>

      <div className="metadata-grid">
        <div className="meta-item">
          <span className="meta-label">Analysis ID:</span>
          <span className="meta-value font-mono">{analysisId}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Dataset:</span>
          <span className="meta-value">{source.dataset_name}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Resource Counts:</span>
          <span className="meta-value">
            Patient: {source.resource_counts.Patient} | Coverage: {source.resource_counts.Coverage} | EOB: {source.resource_counts.ExplanationOfBenefit}
          </span>
        </div>
      </div>

      <h3 className="subsection-title">Loaded Source Files</h3>
      <div className="table-container" tabIndex={0} role="region" aria-label="Loaded source files table">
        <table className="data-table">
          <thead>
            <tr>
              <th scope="col">Alias</th>
              <th scope="col">Path</th>
              <th scope="col">SHA256</th>
              <th scope="col">Size</th>
            </tr>
          </thead>
          <tbody>
            {source.files.map((file) => (
              <tr key={file.alias}>
                <td className="font-semibold">{file.alias}</td>
                <td className="font-mono">{file.path}</td>
                <td className="font-mono text-xs">{file.sha256}</td>
                <td>{file.size_bytes.toLocaleString()} bytes</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
