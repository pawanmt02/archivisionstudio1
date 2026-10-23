import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { projectApi } from '../api/projectApi';
import { Plus, Folder, Trash2, Clock, ArrowRight, LayoutDashboard, Hexagon } from 'lucide-react';

const CARD_GRADIENTS = [
  'linear-gradient(135deg, #0f2027, #203a43, #2c5364)',
  'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
  'linear-gradient(135deg, #0d0d0d, #1a1a1a, #2d6a4f)',
  'linear-gradient(135deg, #2d1b69, #11998e, #38ef7d)',
  'linear-gradient(135deg, #1e3c72, #2a5298, #1e3c72)',
  'linear-gradient(135deg, #4a0000, #8b0000, #cc0000)',
];

const DashboardPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  const fetchProjects = async () => {
    try {
      const res = await projectApi.list();
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async () => {
    const title = newTitle.trim() || 'Untitled Project';
    setCreating(true);
    try {
      const res = await projectApi.create({ title });
      navigate(`/studio/${res.data.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
      setShowModal(false);
      setNewTitle('');
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this project? This cannot be undone.')) return;
    try {
      await projectApi.delete(id);
      setProjects(projects.filter(p => p.id !== id));
    } catch (err) { console.error(err); }
  };

  const formatDate = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  return (
    <div className="dashboard-page">
      {/* Hero header */}
      <div className="dashboard-hero">
        <div className="dashboard-hero-left">
          <div className="dashboard-greeting">Welcome back, <span className="accent">{user?.username}</span></div>
          <h1 className="dashboard-title">Your Design Workspace</h1>
          <p className="dashboard-subtitle">AI-powered architectural synthesis studio. Create, sketch, and render.</p>
        </div>
        <button className="btn-create-project" onClick={() => setShowModal(true)}>
          <Plus size={20} />
          New Project
        </button>
      </div>

      {/* Stats bar */}
      <div className="dashboard-stats">
        <div className="stat-card glass-panel">
          <LayoutDashboard size={20} style={{ color: 'var(--accent-teal)' }} />
          <div>
            <div className="stat-value">{projects.length}</div>
            <div className="stat-label">Projects</div>
          </div>
        </div>
        <div className="stat-card glass-panel">
          <Hexagon size={20} style={{ color: 'var(--accent-violet)' }} />
          <div>
            <div className="stat-value">AI</div>
            <div className="stat-label">ControlNet + SD v1.5</div>
          </div>
        </div>
        <div className="stat-card glass-panel">
          <Clock size={20} style={{ color: '#f59e0b' }} />
          <div>
            <div className="stat-value">2</div>
            <div className="stat-label">Generation Modes</div>
          </div>
        </div>
      </div>

      {/* Section title */}
      <div className="section-header">
        <h2 className="section-title">Recent Projects</h2>
        <span className="section-count">{projects.length} total</span>
      </div>

      {/* Projects */}
      {loading ? (
        <div className="loading-grid">
          {[1,2,3].map(i => <div key={i} className="project-card-skeleton glass-panel" />)}
        </div>
      ) : projects.length === 0 ? (
        <div className="empty-dashboard glass-panel">
          <div className="empty-icon-wrap">
            <Folder size={52} />
          </div>
          <h3>No projects yet</h3>
          <p>Start your first architectural design project</p>
          <button className="btn-primary" style={{ marginTop: 20 }} onClick={() => setShowModal(true)}>
            <Plus size={16} /> Create First Project
          </button>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((project, idx) => (
            <div
              key={project.id}
              className="project-card"
              onClick={() => navigate(`/studio/${project.id}`)}
            >
              {/* Card thumbnail */}
              <div className="project-card-thumb" style={{ background: CARD_GRADIENTS[idx % CARD_GRADIENTS.length] }}>
                <div className="project-card-overlay">
                  <ArrowRight size={28} />
                </div>
                <div className="project-card-badge">
                  {project.canvas_json_state ? 'ACTIVE' : 'NEW'}
                </div>
              </div>

              {/* Card body */}
              <div className="project-card-body">
                <div className="project-card-top">
                  <div className="project-card-title">{project.title}</div>
                  <button
                    className="btn-icon delete-btn"
                    onClick={(e) => handleDelete(e, project.id)}
                    title="Delete project"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
                <div className="project-card-meta">
                  <Clock size={12} />
                  <span>Updated {formatDate(project.updated_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create project modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box glass-panel" onClick={e => e.stopPropagation()}>
            <h2 className="modal-title">New Project</h2>
            <p className="modal-desc">Give your architectural project a name</p>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Modern Villa Interior"
              value={newTitle}
              onChange={e => setNewTitle(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleCreate()}
              autoFocus
              style={{ width: '100%', marginBottom: 16 }}
            />
            <div className="modal-actions">
              <button className="btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleCreate} disabled={creating}>
                {creating ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
