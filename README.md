# 🏛️ Archivision Studio

**Dual-Conditioned Generative Framework for Spatially Constrained Architectural Synthesis**

> An enterprise-grade AI workspace that bridges creative ideation and structural precision — powered by ControlNet, Stable Diffusion v1.5, and a custom Canny-Edge IoU evaluation engine.

---

## ✦ Project Overview

Archivision Studio implements a **Dual-Mode Generative Pipeline**:

| Mode | Engine | Spatial Control | Evaluation |
|------|--------|----------------|------------|
| **Sketch-to-Image** | ControlNet Scribble + SD v1.5 | ✅ Hard geometric constraint | Canny-Edge IoU metric |
| **Text-to-Image** | Stable Diffusion v1.5 | ❌ Stochastic / creative | N/A |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER — React 18 SPA (Vite)                       │
│  HTML5 Canvas · SVG Perspective Grid · Comparison Slider        │
│  Edge Metrics Viewer · Render History Gallery                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP + Bearer JWT
┌──────────────────────────▼──────────────────────────────────────┐
│  APPLICATION LAYER — Python FastAPI (Local)                     │
│  Auth (JWT/bcrypt) · Projects CRUD · OpenCV Pre-processor       │
│  Canny-Edge IoU Evaluator · Prompt Matrix · Colab Dispatcher    │
│  SQLite + SQLAlchemy ORM                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP (ngrok tunnel, optional)
┌──────────────────────────▼──────────────────────────────────────┐
│  INFERENCE LAYER — Google Colab T4 GPU                          │
│  Stable Diffusion v1.5 + ControlNet Scribble (FP16)             │
│  FastAPI server · ngrok public URL · UniPC Scheduler            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
archivision-studio/
├── backend_local/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint, CORS, startup
│   │   ├── config.py             # Pydantic Settings (env-configurable)
│   │   ├── database.py           # SQLAlchemy engine + SQLite
│   │   ├── models/               # user.py, project.py, render.py
│   │   ├── schemas/              # auth, project, render Pydantic schemas
│   │   ├── routers/              # auth.py, workspace.py, synthesis.py
│   │   ├── services/
│   │   │   ├── cv_preprocessor.py   # OpenCV binarization + dilation
│   │   │   ├── evaluator.py         # Canny-Edge IoU calculation
│   │   │   ├── prompt_matrix.py     # Architectural style prompt matrices
│   │   │   └── colab_client.py      # Async Colab dispatcher + local fallback
│   │   └── utils/security.py        # bcrypt + JWT encode/decode
│   ├── requirements.txt
│   └── run.py
│
├── frontend_react/
│   ├── src/
│   │   ├── api/                  # axiosClient, authApi, projectApi, renderApi
│   │   ├── context/AuthContext.jsx
│   │   ├── components/
│   │   │   ├── canvas/           # SketchCanvas, PerspectiveGrid, CanvasToolbar
│   │   │   ├── viewer/           # ComparisonSlider, EdgeMetricsViewer, RenderGallery
│   │   │   └── common/           # Navbar, TunnelConfigModal, StyleSelector
│   │   └── pages/                # LoginPage, RegisterPage, DashboardPage, StudioWorkspace
│   └── package.json
│
└── cloud_inference/
    ├── archivision_t4_engine.ipynb   # Google Colab notebook (ready to upload)
    └── colab_script.py               # Standalone server script
```

---

## 🚀 Quick Start

### Step 1 — Backend Setup

```powershell
cd backend_local

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python run.py
```

The API will be available at **http://localhost:8000**
Swagger UI: **http://localhost:8000/docs**

---

### Step 2 — Frontend Setup

```powershell
cd frontend_react

npm install
npm run dev
```

The app will be available at **http://localhost:5173**

---

### Step 3 — Cloud GPU (Optional, for real AI generation)

> Without this step, the system uses **Local Fallback Mode** which returns placeholder images. All other features (auth, projects, CV pipeline, IoU metric) work fully.

1. Open `cloud_inference/archivision_t4_engine.ipynb` in Google Colab
2. Set **Runtime → Change runtime type → T4 GPU**
3. Get a free ngrok token at https://dashboard.ngrok.com
4. Paste your token into **Cell 4**: `NGROK_AUTH_TOKEN = "your-token-here"`
5. Run all cells (**Runtime → Run all**)
6. Copy the public URL printed in Cell 6 output
7. In Archivision Studio, click the **⚙ GPU Tunnel** button in the navbar
8. Paste the URL and click Save

---

## 🔬 Scientific CV Pipeline

### OpenCV Preprocessing (`cv_preprocessor.py`)

```
Raw Sketch (any resolution, RGBA)
   ↓ Resize to 512×512
   ↓ Grayscale conversion
   ↓ Gaussian Blur (3×3 kernel)
   ↓ Otsu Binarization
   ↓ Morphological Dilation (3×3 kernel, 2 iterations) ← closes broken strokes
   ↓ Invert → white-lines-on-black (ControlNet Scribble format)
   ↓ Convert back to BGR 3-channel
→ Cleaned Geometric Map
```

### Canny-Edge IoU Evaluator (`evaluator.py`)

$$\text{IoU} = \frac{|A \cap B|}{|A \cup B|}$$

Where $A$ = edge mask of input sketch, $B$ = edge mask of rendered output.

**Edge Overlay Composite:**
- 🟢 **Green** — exact edge overlap (correct structural prediction)
- 🔴 **Red** — missing strokes (hallucinated or omitted geometry)
- 🔵 **Blue** — hallucinated edges (noise in render not in sketch)

---

## 🎨 Architectural Style Presets

| Style | Description |
|-------|-------------|
| **Photorealistic** | 8K architectural photograph, sharp focus, Unreal Engine 5 render |
| **Brutalism** | Exposed concrete, geometric forms, harsh shadows, monolithic |
| **Minimalist** | Clean lines, white walls, Scandinavian design, natural light |
| **Biophilic** | Living walls, natural materials, organic forms, sustainable |
| **Industrial** | Exposed pipes, brick walls, Edison bulbs, warehouse loft |
| **Art Deco** | Geometric patterns, gold accents, 1920s glamour, ornate |
| **Futuristic** | Parametric design, curved surfaces, smart glass, Zaha Hadid |

---

## 🔒 Security

- Passwords hashed with **bcrypt** (passlib)
- API routes protected with **JWT Bearer tokens** (python-jose)
- Tokens expire after **24 hours** by default
- CORS restricted to `localhost:5173` and `localhost:3000`

---

## 🗄️ Database Schema

```sql
-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Projects (1 User : Many Projects)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) DEFAULT 'Untitled Project',
    canvas_json_state TEXT,
    updated_at DATETIME
);

-- Render History (1 Project : Many Renders)
CREATE TABLE render_history (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    generation_mode VARCHAR(20) NOT NULL,  -- 'sketch' | 'text'
    prompt_or_style TEXT,
    sketch_image_b64 TEXT,
    rendered_image_b64 TEXT,
    edge_overlay_b64 TEXT,
    inference_latency_seconds FLOAT,
    edge_similarity_score FLOAT,           -- IoU: 0.0–1.0
    seed_used INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ Environment Variables

Create a `.env` file in `backend_local/` to override defaults:

```env
SECRET_KEY=your-super-secret-production-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./archivision.db
COLAB_TUNNEL_URL=https://xxxx.ngrok.io
CORS_ORIGINS=["http://localhost:5173"]
```

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Login, receive JWT token |
| GET | `/auth/me` | Get current user info |
| GET | `/projects/` | List all user projects |
| POST | `/projects/` | Create new project |
| GET | `/projects/{id}` | Get project details |
| PUT | `/projects/{id}` | Update title / canvas state |
| DELETE | `/projects/{id}` | Delete project + renders |
| GET | `/projects/{id}/renders` | Get render history |
| POST | `/synthesis/generate` | Generate image (sketch or text mode) |
| GET | `/synthesis/tunnel-status` | Check Colab tunnel connectivity |
| POST | `/synthesis/tunnel-config` | Update tunnel URL at runtime |

---

## 🏅 Non-Functional Requirements

| Requirement | Implementation |
|-------------|---------------|
| **Latency** | Async FastAPI + `asyncio` background dispatch; GPU returns in 5–15s |
| **Security** | bcrypt passwords, JWT Bearer auth on all protected routes |
| **Scalability** | Non-blocking `async def` routes, thread pool for CV operations |
| **Determinism** | Seed locking persisted per render in DB |
| **Hardware** | No local GPU required; client needs any HTML5/WebGL browser |

---

*Built as part of Archivision Studio PDR — Enterprise Generative AI Architectural Workspace.*
