import React from 'react';

const styles = [
  { id: 'Photorealistic', label: 'Photorealistic', icon: '📸', color: '#0ea5e9', desc: 'Highly detailed, ultra-realistic render' },
  { id: 'Brutalism',      label: 'Brutalism',      icon: '🏢', color: '#64748b', desc: 'Raw concrete, geometric forms' },
  { id: 'Minimalist',    label: 'Minimalist',    icon: '✨', color: '#14b8a6', desc: 'Clean lines, open spaces' },
  { id: 'Biophilic',     label: 'Biophilic',     icon: '🌿', color: '#22c55e', desc: 'Nature-integrated design' },
  { id: 'Industrial',    label: 'Industrial',    icon: '⚙️',  color: '#f97316', desc: 'Exposed pipes and materials' },
  { id: 'Art Deco',      label: 'Art Deco',      icon: '🎭', color: '#a855f7', desc: 'Geometric, ornamental luxury' },
  { id: 'Futuristic',    label: 'Futuristic',    icon: '🚀', color: '#6366f1', desc: 'Sleek, sci-fi architecture' },
];

const StyleSelector = ({ selectedStyle, onChange }) => {
  return (
    <div className="panel-section">
      <div className="panel-title">Style Preset</div>
      <div className="style-grid">
        {styles.map(style => (
          <div
            key={style.id}
            className={`style-card ${selectedStyle === style.id ? 'active' : ''}`}
            onClick={() => onChange(style.id)}
            title={style.desc}
            style={{ '--style-color': style.color }}
          >
            <span className="style-icon">{style.icon}</span>
            <span className="style-label">{style.label}</span>
            {selectedStyle === style.id && (
              <span className="style-check">✓</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StyleSelector;
