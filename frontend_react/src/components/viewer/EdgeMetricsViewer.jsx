import React from 'react';
import { Copy } from 'lucide-react';

const toDataUrl = (b64) => {
  if (!b64) return null;
  if (b64.startsWith('data:')) return b64;
  return `data:image/png;base64,${b64}`;
};

const EdgeMetricsViewer = ({ edgeOverlayB64, iouScore, latency, seedUsed, mode }) => {
  const isTextMode = mode === 'text';

  // Score colour thresholds for Structural Fidelity (higher = better)
  let scoreColor = 'metric-poor';
  if (iouScore >= 0.7)      scoreColor = 'metric-good';
  else if (iouScore >= 0.4) scoreColor = 'metric-fair';

  const scoreLabel = iouScore != null ? `${(iouScore * 100).toFixed(1)}%` : 'N/A';

  const metaRow = (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-secondary)', marginTop: 8 }}>
      <span>Latency: {latency ? `${latency.toFixed(2)}s` : 'N/A'}</span>
      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        Seed: {seedUsed ?? 'N/A'}
        {seedUsed && (
          <button className="btn-icon" style={{ padding: '2px' }}
            onClick={() => navigator.clipboard.writeText(String(seedUsed))} title="Copy seed">
            <Copy size={12} />
          </button>
        )}
      </span>
    </div>
  );

  if (isTextMode) {
    return (
      <div className="metrics-card" style={{ marginTop: 10, padding: '12px 14px' }}>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', marginBottom: 4 }}>
          Edge Fidelity — Sketch mode only
        </div>
        {metaRow}
      </div>
    );
  }

  return (
    <div className="metrics-card" style={{ marginTop: 10 }}>
      {/* Header */}
      <div className="panel-title" style={{ fontSize: 12, marginBottom: 8 }}>
        Structural Fidelity Score
      </div>

      {/* Edge overlay image */}
      {edgeOverlayB64 ? (
        <img
          src={toDataUrl(edgeOverlayB64)}
          alt="Edge Overlay"
          className="edge-overlay-preview"
        />
      ) : (
        <div className="edge-overlay-preview"
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>Processing...</span>
        </div>
      )}

      {/* Big score number */}
      {iouScore != null && (
        <div className={`metric-iou ${scoreColor}`} style={{ fontSize: 32, fontWeight: 800, textAlign: 'center', margin: '8px 0' }}>
          {scoreLabel}
        </div>
      )}

      {/* What score means */}
      <div style={{
        background: 'rgba(0,0,0,0.3)', borderRadius: 6, padding: '6px 10px',
        fontSize: 10, color: 'var(--text-secondary)', marginBottom: 6, lineHeight: 1.5,
      }}>
        {iouScore >= 0.7 ? '🟢 Excellent — AI faithfully reproduced your design'
          : iouScore >= 0.4 ? '🟡 Good — Most sketch edges preserved in render'
          : iouScore >= 0.15 ? '🟠 Fair — Key structural lines preserved'
          : '🔴 Low — Draw more detailed sketches for higher fidelity'}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 10, fontSize: 10, color: 'var(--text-muted)', flexWrap: 'wrap', marginBottom: 4 }}>
        <span><span style={{ display: 'inline-block', width: 8, height: 8, background: '#00ff00', marginRight: 3, borderRadius: 2 }} />Preserved</span>
        <span><span style={{ display: 'inline-block', width: 8, height: 8, background: '#ff0000', marginRight: 3, borderRadius: 2 }} />Missed</span>
        <span><span style={{ display: 'inline-block', width: 8, height: 8, background: '#0000ff', marginRight: 3, borderRadius: 2 }} />AI Added</span>
      </div>

      {metaRow}
    </div>
  );
};

export default EdgeMetricsViewer;
