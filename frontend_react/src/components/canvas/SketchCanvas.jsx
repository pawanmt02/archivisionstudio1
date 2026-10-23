import React, { useRef, useState, useEffect, useImperativeHandle, forwardRef } from 'react';

const SketchCanvas = forwardRef(({ width = 512, height = 512 }, ref) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState('draw');
  const [strokeWidth, setStrokeWidth] = useState(2);
  const [strokeColor, setStrokeColor] = useState('#000000');
  const [history, setHistory] = useState([]);
  
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [previewCanvas, setPreviewCanvas] = useState(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);
      saveHistoryState(canvas);
      
      const pCanvas = document.createElement('canvas');
      pCanvas.width = width;
      pCanvas.height = height;
      setPreviewCanvas(pCanvas);
    }
  }, [width, height]);

  const saveHistoryState = (canvas) => {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, width, height);
    setHistory((prev) => [...prev, imageData]);
  };

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    return {
      x: (clientX - rect.left) * (canvas.width / rect.width),
      y: (clientY - rect.top) * (canvas.height / rect.height)
    };
  };

  const startDrawing = (e) => {
    e.preventDefault();
    const { x, y } = getCoordinates(e);
    setIsDrawing(true);
    setStartPos({ x, y });

    const ctx = canvasRef.current.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineWidth = strokeWidth;
    ctx.strokeStyle = tool === 'eraser' ? '#ffffff' : strokeColor;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    if (tool === 'draw' || tool === 'eraser') {
      ctx.lineTo(x, y);
      ctx.stroke();
    }
  };

  const draw = (e) => {
    e.preventDefault();
    if (!isDrawing) return;
    const { x, y } = getCoordinates(e);
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (tool === 'draw' || tool === 'eraser') {
      ctx.lineTo(x, y);
      ctx.stroke();
    } else if (tool === 'line' || tool === 'rect') {
      const pCtx = previewCanvas.getContext('2d');
      pCtx.clearRect(0, 0, width, height);
      pCtx.drawImage(canvas, 0, 0);
      
      pCtx.beginPath();
      pCtx.lineWidth = strokeWidth;
      pCtx.strokeStyle = strokeColor;
      pCtx.lineCap = 'round';
      
      if (tool === 'line') {
        pCtx.moveTo(startPos.x, startPos.y);
        pCtx.lineTo(x, y);
      } else if (tool === 'rect') {
        pCtx.rect(startPos.x, startPos.y, x - startPos.x, y - startPos.y);
      }
      pCtx.stroke();
      
      const realCtx = canvas.getContext('2d');
      realCtx.clearRect(0, 0, width, height);
      realCtx.drawImage(previewCanvas, 0, 0);
    }
  };

  const stopDrawing = (e) => {
    e.preventDefault();
    if (!isDrawing) return;
    setIsDrawing(false);
    saveHistoryState(canvasRef.current);
  };

  useImperativeHandle(ref, () => ({
    setTool,
    setStrokeWidth,
    setStrokeColor,
    tool,
    strokeWidth,
    strokeColor,
    undo: () => {
      if (history.length > 1) {
        const newHistory = [...history];
        newHistory.pop(); // remove current state
        const prevState = newHistory[newHistory.length - 1];
        const ctx = canvasRef.current.getContext('2d');
        ctx.putImageData(prevState, 0, 0);
        setHistory(newHistory);
      }
    },
    clear: () => {
      const ctx = canvasRef.current.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);
      saveHistoryState(canvasRef.current);
    },
    exportCanvas: () => {
      return canvasRef.current.toDataURL('image/png');
    },
    getStrokeCount: () => {
      return history.length - 1;
    },
    getComplexityScore: () => {
      const ctx = canvasRef.current.getContext('2d');
      const imgData = ctx.getImageData(0, 0, width, height).data;
      let drawnPixels = 0;
      // imgData is a flat array of RGBA values [r,g,b,a, r,g,b,a, ...]
      for (let i = 0; i < imgData.length; i += 4) {
        // If a pixel is not completely white (e.g., r, g, or b is < 250)
        if (imgData[i] < 250 || imgData[i+1] < 250 || imgData[i+2] < 250) {
          drawnPixels++;
        }
      }
      return drawnPixels;
    }
  }));

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="canvas-layer interactive"
      onMouseDown={startDrawing}
      onMouseMove={draw}
      onMouseUp={stopDrawing}
      onMouseOut={stopDrawing}
      onTouchStart={startDrawing}
      onTouchMove={draw}
      onTouchEnd={stopDrawing}
      style={{ touchAction: 'none' }}
    />
  );
});

export default SketchCanvas;
