import React, { useState } from 'react';
import { Maximize, X } from 'lucide-react';

const toDataUrl = (b64) => {
  if (!b64) return null;
  if (b64.startsWith('data:')) return b64;
  return `data:image/png;base64,${b64}`;
};

const RenderGallery = ({ renders, onSelect, selectedId }) => {
  const [hovered, setHovered] = useState(null);
  const [fullscreenImage, setFullscreenImage] = useState(null);

  if (!renders || renders.length === 0) return null;

  const FullscreenModal = () => (
    <div 
      onClick={() => setFullscreenImage(null)}
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'rgba(0, 0, 0, 0.9)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        backdropFilter: 'blur(10px)',
        animation: 'fadeIn 0.2s ease',
        cursor: 'zoom-out'
      }}
    >
      <div 
        style={{
          position: 'absolute', top: 20, right: 20,
          background: 'rgba(255,255,255,0.1)', padding: 10,
          borderRadius: '50%', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}
        onClick={(e) => {
          e.stopPropagation();
          setFullscreenImage(null);
        }}
      >
        <X color="white" size={24} />
      </div>
      <img
        src={fullscreenImage}
        alt="Render Fullscreen"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '90vw', maxHeight: '90vh',
          objectFit: 'contain',
          borderRadius: 8,
          boxShadow: '0 0 40px rgba(0,0,0,0.5)',
          cursor: 'default'
        }}
      />
    </div>
  );

  return (
    <div className="panel-section">
      <div className="panel-title">History</div>
      <div className="gallery-grid">
        {renders.map((render) => {
          const mode = render.generation_mode || render.mode || 'sketch';
          const iou  = render.edge_similarity_score ?? render.iou_score;
          const imgSrc = toDataUrl(render.rendered_image_b64 || render.sketch_image_b64);
          const isSelected = selectedId === render.id;
          const isHovered  = hovered === render.id;

          return (
            <div
              key={render.id}
              className={`gallery-card ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelect(render)}
              onMouseEnter={() => setHovered(render.id)}
              onMouseLeave={() => setHovered(null)}
              style={{
                transform: isHovered ? 'scale(1.04)' : 'scale(1)',
                transition: 'transform 0.18s ease, box-shadow 0.18s ease',
                boxShadow: isHovered ? '0 6px 20px rgba(0,0,0,0.4)' : undefined,
                position: 'relative',
              }}
            >
              {imgSrc ? (
                <img
                  src={imgSrc}
                  alt="Render thumbnail"
                  className="gallery-image"
                  style={{ animation: 'fadeInThumb 0.4s ease' }}
                />
              ) : (
                <div className="gallery-image" style={{
                  background: 'var(--bg-surface)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <span style={{ fontSize: 18, opacity: 0.3 }}>🖼</span>
                </div>
              )}

              {/* Hover overlay with Maximize */}
              {isHovered && (
                <div style={{
                  position: 'absolute', inset: 0, borderRadius: 6,
                  background: 'rgba(0,0,0,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'white', fontSize: 11, fontWeight: 600, letterSpacing: 0.5,
                }}>
                  <div 
                    onClick={(e) => {
                      e.stopPropagation();
                      setFullscreenImage(imgSrc);
                    }}
                    style={{
                      background: 'rgba(0,0,0,0.6)', padding: 6,
                      borderRadius: '50%', cursor: 'pointer', zIndex: 10,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                    title="View Fullscreen"
                  >
                    <Maximize size={16} />
                  </div>
                </div>
              )}

              <div className="gallery-info">
                <span className={`badge ${mode === 'text' ? 'badge-text' : 'badge-sketch'}`}>
                  {mode.toUpperCase()}
                </span>
                {iou != null && (
                  <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
                    {(iou * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
      {fullscreenImage && <FullscreenModal />}
    </div>
  );
};

export default RenderGallery;
