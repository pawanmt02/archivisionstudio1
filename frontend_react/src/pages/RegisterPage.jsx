import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/authApi';
import { Eye, EyeOff } from 'lucide-react';

const RegisterPage = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      return setError('Passwords do not match');
    }
    if (formData.password.length < 6) {
      return setError('Password must be at least 6 characters');
    }

    setLoading(true);
    try {
      await authApi.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      const res = await authApi.login({ username: formData.username, password: formData.password });
      await login(res.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (err.response?.status === 400) {
        setError('Username or email already registered. Try logging in instead.');
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Registration failed. Make sure backend is running at port 8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Animated background orbs */}
      <div className="auth-orb auth-orb-1" />
      <div className="auth-orb auth-orb-2" />

      <div className="auth-card glass-panel">
        {/* Logo */}
        <div className="auth-logo">
          <span style={{ fontSize: 28 }}>⬡</span>
        </div>
        <h1 className="auth-title">Create Account</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, textAlign: 'center', marginBottom: 24 }}>
          Join Archivision Studio
        </p>

        {error && (
          <div className="error-msg" style={{ marginBottom: 16, padding: '10px 14px', borderRadius: 8, background: 'rgba(224,90,90,0.12)', border: '1px solid rgba(224,90,90,0.3)', color: '#e05a5a', fontSize: 13 }}>
            ⚠ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="input-group">
            <label className="input-label">Username</label>
            <input
              type="text" name="username" className="input-field"
              value={formData.username} onChange={handleChange}
              placeholder="e.g. pawan123" required autoComplete="username"
            />
          </div>

          <div className="input-group">
            <label className="input-label">Email</label>
            <input
              type="email" name="email" className="input-field"
              value={formData.email} onChange={handleChange}
              placeholder="your@email.com" required autoComplete="email"
            />
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPass ? 'text' : 'password'} name="password"
                className="input-field" value={formData.password}
                onChange={handleChange} placeholder="Min 6 characters"
                required autoComplete="new-password"
                style={{ paddingRight: 40 }}
              />
              <button type="button" onClick={() => setShowPass(!showPass)}
                style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Confirm Password</label>
            <input
              type={showPass ? 'text' : 'password'} name="confirmPassword"
              className="input-field" value={formData.confirmPassword}
              onChange={handleChange} placeholder="Repeat password"
              required autoComplete="new-password"
            />
          </div>

          <button type="submit" className="auth-submit-btn" disabled={loading}
            style={{ marginTop: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            {loading ? (
              <><span className="btn-spinner" style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 0.8s linear infinite', display: 'inline-block' }} /> Registering...</>
            ) : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--accent-teal)', textDecoration: 'none', fontWeight: 600 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
