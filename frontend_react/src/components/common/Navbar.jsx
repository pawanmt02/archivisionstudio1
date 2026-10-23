import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Hexagon, LogOut, Cpu, ChevronRight, Save } from 'lucide-react';

const Navbar = ({ projectTitle, onTitleChange, mode, setMode, tunnelConnected, onOpenTunnelConfig, onSave, saving }) => {
  const { user, logout } = useAuth();

  return (
    <div className="studio-navbar">
      {/* Left — Logo + Project Title */}
      <div className="navbar-left">
        <div className="navbar-brand">
          <Hexagon size={22} strokeWidth={1.5} />
          <span>ARCHIVISION</span>
        </div>
        <div className="navbar-divider" />
        <ChevronRight size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
        <input
          type="text"
          value={projectTitle || ''}
          onChange={(e) => onTitleChange(e.target.value)}
          className="navbar-title-input"
          placeholder="Untitled Project"
          spellCheck={false}
        />
        {onSave && (
          <button
            className="navbar-save-btn"
            onClick={onSave}
            disabled={saving}
            title="Save project"
          >
            <Save size={14} />
            {saving ? 'Saving...' : 'Save'}
          </button>
        )}
      </div>

      {/* Center — Mode toggle */}
      <div className="mode-toggle">
        <button
          className={mode === 'sketch' ? 'active' : ''}
          onClick={() => setMode('sketch')}
        >
          ✏️ SKETCH
        </button>
        <button
          className={mode === 'text' ? 'active' : ''}
          onClick={() => setMode('text')}
        >
          💬 TEXT
        </button>
      </div>

      {/* Right — Tunnel + User */}
      <div className="navbar-right">
        <button
          className={`tunnel-btn ${tunnelConnected ? 'tunnel-on' : 'tunnel-off'}`}
          onClick={onOpenTunnelConfig}
          title="Configure GPU Tunnel"
        >
          <Cpu size={15} />
          <span className={`tunnel-dot ${tunnelConnected ? 'dot-on' : 'dot-off'}`} />
          {tunnelConnected ? 'GPU Connected' : 'GPU Tunnel'}
        </button>

        <div className="navbar-user">
          <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <span className="user-name">{user?.username}</span>
          <button className="btn-icon" onClick={logout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
