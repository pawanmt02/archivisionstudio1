"""
Archivision Studio - Cloud Inference Engine
Deploy this on Google Colab with T4 GPU runtime.

Setup:
  !pip install diffusers transformers accelerate controlnet_aux pyngrok fastapi uvicorn[standard] torch torchvision pillow python-multipart xformers
  !python colab_script.py
"""

import os
import time
import base64
import asyncio
import io
import threading
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import torch
from PIL import Image
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyngrok import ngrok

# Diffusers imports
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
)

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")  # Set via env or hardcode for testing
PORT = 8000
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# Model IDs
SD_MODEL_ID = "runwayml/stable-diffusion-v1-5"
CONTROLNET_MODEL_ID = "lllyasviel/sd-controlnet-scribble"

# ─────────────────────────────────────────────────────────────
# Pydantic Request/Response Models
# ─────────────────────────────────────────────────────────────

class SketchRequest(BaseModel):
    sketch_base64: str
    positive_prompt: str
    negative_prompt: str = ""
    seed: int = -1  # -1 means random
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    controlnet_conditioning_scale: float = 0.8


class TextRequest(BaseModel):
    positive_prompt: str
    negative_prompt: str = ""
    seed: int = -1
    num_inference_steps: int = 30
    guidance_scale: float = 7.5


class GenerationResponse(BaseModel):
    image_base64: str
    seed_used: int
    latency_seconds: float


class HealthResponse(BaseModel):
    status: str
    gpu: str
    vram_gb: float
    models_loaded: bool


# ─────────────────────────────────────────────────────────────
# Global model references
# ─────────────────────────────────────────────────────────────
controlnet_pipe: Optional[StableDiffusionControlNetPipeline] = None
text_pipe: Optional[StableDiffusionPipeline] = None
_models_loaded: bool = False


# ─────────────────────────────────────────────────────────────
# Model Loading
# ─────────────────────────────────────────────────────────────

def load_models() -> None:
    global controlnet_pipe, text_pipe, _models_loaded

    print(f"[Archivision] Device: {DEVICE}  |  dtype: {DTYPE}")

    print("[Archivision] Loading ControlNet (scribble) model...")
    controlnet = ControlNetModel.from_pretrained(
        CONTROLNET_MODEL_ID,
        torch_dtype=DTYPE,
    )
    print("[Archivision] ControlNet loaded ✓")

    print("[Archivision] Loading Stable Diffusion ControlNet pipeline...")
    controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(
        SD_MODEL_ID,
        controlnet=controlnet,
        torch_dtype=DTYPE,
        safety_checker=None,
        requires_safety_checker=False,
    )
    controlnet_pipe.scheduler = UniPCMultistepScheduler.from_config(
        controlnet_pipe.scheduler.config
    )
    try:
        controlnet_pipe.enable_xformers_memory_efficient_attention()
        print("[Archivision] xformers memory-efficient attention enabled ✓")
    except Exception:
        print("[Archivision] xformers not available — using default attention")
    controlnet_pipe = controlnet_pipe.to(DEVICE)
    print("[Archivision] ControlNet pipeline ready ✓")

    print("[Archivision] Loading Text-to-Image pipeline...")
    text_pipe = StableDiffusionPipeline.from_pretrained(
        SD_MODEL_ID,
        torch_dtype=DTYPE,
        safety_checker=None,
        requires_safety_checker=False,
    )
    text_pipe.scheduler = UniPCMultistepScheduler.from_config(
        text_pipe.scheduler.config
    )
    try:
        text_pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass
    text_pipe = text_pipe.to(DEVICE)
    print("[Archivision] Text-to-Image pipeline ready ✓")

    _models_loaded = True
    print("[Archivision] ✅ All models loaded and ready.")


# ─────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────

def decode_sketch(b64: str) -> Image.Image:
    """Decode base64 string to a 512x512 RGB PIL Image."""
    # Strip data URL prefix if present (e.g. "data:image/png;base64,")
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((512, 512), Image.LANCZOS)
    return img


def encode_image(img: Image.Image) -> str:
    """Encode a PIL Image to a base64 PNG string."""
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def get_generator(seed: int):
    """Create a deterministic torch Generator. seed=-1 generates a random seed."""
    generator = torch.Generator(device=DEVICE)
    if seed == -1:
        seed = int(torch.randint(0, 2**32 - 1, (1,)).item())
    generator.manual_seed(seed)
    return generator, seed


# ─────────────────────────────────────────────────────────────
# FastAPI application with lifespan model loading
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models in a thread pool so we don't block the event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_models)
    yield
    # Cleanup on shutdown
    print("[Archivision] Shutting down inference engine.")


app = FastAPI(
    title="Archivision T4 Engine",
    version="1.0.0",
    description=(
        "Cloud inference API for Archivision Studio. "
        "Runs Stable Diffusion v1.5 + ControlNet Scribble on NVIDIA T4 GPU."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint for status check."""
    return {
        "status": "online",
        "message": "Archivision T4 Engine is running! Paste this URL into Archivision Studio settings."
    }

@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health() -> HealthResponse:
    """Return GPU info and model load status."""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = round(
            torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2
        )
    else:
        gpu_name = "CPU (no CUDA)"
        vram_gb = 0.0
    return HealthResponse(
        status="healthy",
        gpu=gpu_name,
        vram_gb=vram_gb,
        models_loaded=_models_loaded,
    )


@app.post("/generate_sketch", response_model=GenerationResponse, tags=["Generation"])
async def generate_sketch(req: SketchRequest) -> GenerationResponse:
    """
    Sketch-to-Image generation using ControlNet Scribble.
    Accepts a preprocessed (binarized, dilated) sketch as base64.
    """
    if not _models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models are still loading. Please retry in a few seconds."
        )
    try:
        sketch_image = decode_sketch(req.sketch_base64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid sketch_base64: {exc}")

    generator, seed_used = get_generator(req.seed)

    t0 = time.perf_counter()

    # Run inference in executor to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: controlnet_pipe(
            prompt=req.positive_prompt,
            negative_prompt=req.negative_prompt,
            image=sketch_image,
            generator=generator,
            num_inference_steps=req.num_inference_steps,
            guidance_scale=req.guidance_scale,
            controlnet_conditioning_scale=req.controlnet_conditioning_scale,
            height=512,
            width=512,
        )
    )

    latency = round(time.perf_counter() - t0, 3)
    output_image: Image.Image = result.images[0]

    return GenerationResponse(
        image_base64=encode_image(output_image),
        seed_used=seed_used,
        latency_seconds=latency,
    )


@app.post("/generate_text", response_model=GenerationResponse, tags=["Generation"])
async def generate_text(req: TextRequest) -> GenerationResponse:
    """
    Text-to-Image generation using Stable Diffusion v1.5.
    Pure ideation mode without spatial constraints.
    """
    if not _models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models are still loading. Please retry in a few seconds."
        )

    generator, seed_used = get_generator(req.seed)

    t0 = time.perf_counter()

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: text_pipe(
            prompt=req.positive_prompt,
            negative_prompt=req.negative_prompt,
            generator=generator,
            num_inference_steps=req.num_inference_steps,
            guidance_scale=req.guidance_scale,
            height=512,
            width=512,
        )
    )

    latency = round(time.perf_counter() - t0, 3)
    output_image: Image.Image = result.images[0]

    return GenerationResponse(
        image_base64=encode_image(output_image),
        seed_used=seed_used,
        latency_seconds=latency,
    )


# ─────────────────────────────────────────────────────────────
# Entry point (for direct execution outside Colab)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    else:
        print("⚠️  No NGROK_AUTH_TOKEN set. Running locally only.")

    try:
        tunnel = ngrok.connect(PORT)
        public_url = tunnel.public_url
        print()
        print("=" * 60)
        print("  🏛️  ARCHIVISION T4 ENGINE - ONLINE")
        print(f"  📡 Public URL: {public_url}")
        print(f"  📋 Paste this URL into Archivision Studio Settings")
        print(f"  🔗 API Docs: {public_url}/docs")
        print("=" * 60)
        print()
    except Exception as e:
        print(f"⚠️  ngrok tunnel failed: {e}. Running on localhost only.")
        public_url = f"http://localhost:{PORT}"

    uvicorn.run(app, host="0.0.0.0", port=PORT)
