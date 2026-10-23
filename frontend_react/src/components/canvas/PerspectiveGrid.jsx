import React, { useState } from 'react';

const PerspectiveGrid = ({ visible, width = 512, height = 512, mode = '1-point' }) => {
  const [vp, setVp] = useState({ x: width / 2, y: height / 2 });
  const [isDragging, setIsDragging] = useState(false);

  if (!visible) return null;

  const handleMouseDown = (e) => {
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setVp({ x, y });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const strokeColor = 'rgba(99,198,210,0.25)';
  const strokeWidth = 0.5;

  const lines = [
    { x1: 0, y1: 0 },
    { x1: width, y1: 0 },
    { x1: 0, y1: height },
    { x1: width, y1: height },
    { x1: width / 2, y1: 0 },
    { x1: width / 2, y1: height },
    { x1: 0, y1: height / 2 },
    { x1: width, y1: height / 2 },
  ];

  const horizontals = Array.from({ length: 10 }).map((_, i) => (
    <line key={`h-${i}`} x1={0} y1={(height / 10) * i} x2={width} y2={(height / 10) * i} stroke={strokeColor} strokeWidth={strokeWidth} />
  ));

  return (
    <svg
      width={width}
      height={height}
      className="canvas-layer"
      style={{ pointerEvents: isDragging ? 'auto' : 'none' }}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {horizontals}
      {lines.map((p, i) => (
        <line key={i} x1={p.x1} y1={p.y1} x2={vp.x} y2={vp.y} stroke={strokeColor} strokeWidth={strokeWidth} />
      ))}
      <circle
        cx={vp.x}
        cy={vp.y}
        r={6}
        fill="var(--accent-teal)"
        style={{ pointerEvents: 'auto', cursor: 'grab' }}
        onMouseDown={handleMouseDown}
      />
    </svg>
  );
};

export default PerspectiveGrid;
