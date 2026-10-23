import React from 'react';
import { Pencil, Minus, Square, Eraser, RotateCcw, Trash2, Wand2 } from 'lucide-react';

const tools = [
  { id: 'draw',   icon: <Pencil size={18} />,  label: 'Draw' },
  { id: 'line',   icon: <Minus size={18} />,   label: 'Line' },
  { id: 'rect',   icon: <Square size={18} />,  label: 'Rect' },
  { id: 'eraser', icon: <Eraser size={18} />,  label: 'Erase' },
];

const CanvasToolbar = ({ tool, setTool, strokeWidth, setStrokeWidth, strokeColor, setStrokeColor, onUndo, onClear, onExport }) => {
  return (
    <div className="studio-sidebar">
      {/* Draw tools */}
      <div className="sidebar-section">
        {tools.map(t => (
          <button
            key={t.id}
            className={`sidebar-tool-btn ${tool === t.id ? 'active' : ''}`}
            onClick={() => setTool(t.id)}
            title={t.label}
          >
            {t.icon}
            <span className="tool-label">{t.label}</span>
          </button>
        ))}
      </div>

      <div className="sidebar-divider" />

      {/* Color + Width */}
      <div className="sidebar-section">
        <div className="sidebar-tool-btn" title="Stroke Color" style={{ padding: '6px', flexDirection: 'column', gap: 4 }}>
          <input
            type="color"
            value={strokeColor}
            onChange={(e) => setStrokeColor(e.target.value)}
            style={{ width: 28, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', padding: 0 }}
          />
          <span className="tool-label">Color</span>
        </div>

        <div className="sidebar-tool-btn" style={{ flexDirection: 'column', gap: 4, padding: '8px 4px', cursor: 'default' }} title={`Stroke: ${strokeWidth}px`}>
          <input
            type="range"
            min="1" max="20"
            value={strokeWidth}
            onChange={(e) => setStrokeWidth(parseInt(e.target.value))}
            style={{ writingMode: 'vertical-rl', direction: 'rtl', height: 60, width: 16 }}
          />
          <span className="tool-label">{strokeWidth}px</span>
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Undo + Clear */}
      <div className="sidebar-section">
        <button className="sidebar-tool-btn" onClick={onUndo} title="Undo (Ctrl+Z)">
          <RotateCcw size={18} />
          <span className="tool-label">Undo</span>
        </button>
        <button className="sidebar-tool-btn danger" onClick={onClear} title="Clear Canvas">
          <Trash2 size={18} />
          <span className="tool-label">Clear</span>
        </button>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Generate button */}
      <button className="sidebar-generate-btn" onClick={onExport} title="Generate AI Render">
        <Wand2 size={20} />
        <span className="tool-label" style={{ fontSize: 9, letterSpacing: 1 }}>GENERATE</span>
      </button>
    </div>
  );
};

export default CanvasToolbar;
