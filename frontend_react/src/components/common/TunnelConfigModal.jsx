import React, { useState, useEffect } from 'react';
import { X, ExternalLink } from 'lucide-react';

const TunnelConfigModal = ({ isOpen, onClose, currentUrl, onSave, status }) => {
  const [url, setUrl] = useState('');

  useEffect(() => {
    setUrl(currentUrl || '');
  }, [currentUrl, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content glass-panel">
        <div className="modal-header">
          <div className="modal-title">Cloud GPU Tunnel Configuration</div>
          <button className="btn-icon" onClick={onClose}><X size={20} /></button>
        </div>
        
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '20px' }}>
          Connect to your Colab runtime by pasting the Ngrok URL below. 
          Make sure the notebook is running and the tunnel is active.
        </p>

        <div className="input-group">
          <label className="input-label">Ngrok URL</label>
          <input 
            type="text" 
            className="input-field" 
            placeholder="https://xxxx.ngrok.io" 
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '20px 0' }}>
          <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Status:</span>
          <div className={`status-indicator`} style={{ padding: '2px 8px' }}>
            <div className={`status-dot ${status?.status === 'active' ? 'connected' : 'disconnected'}`}></div>
            {status?.status === 'active' ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={() => { onSave(url); }}>Save & Connect</button>
        </div>
      </div>
    </div>
  );
};

export default TunnelConfigModal;
