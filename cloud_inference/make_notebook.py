"""Generate the Archivision Colab notebook — original working version."""
import json

CELL4_CODE = '''\
# Cell 4 — Load models + Start server (~3-5 min first time)
import os, time, base64, io, threading
import torch
from PIL import Image
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyngrok import ngrok
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler,
)

PORT   = 8787
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
DTYPE  = torch.float16 if DEVICE == 'cuda' else torch.float32
print(f'Device: {DEVICE} | dtype: {DTYPE}')

class SketchRequest(BaseModel):
    sketch_base64: str
    positive_prompt: str
    negative_prompt: str = ''
    seed: int = -1
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    controlnet_conditioning_scale: float = 1.0

class TextRequest(BaseModel):
    positive_prompt: str
    negative_prompt: str = ''
    seed: int = -1
    num_inference_steps: int = 30
    guidance_scale: float = 7.5

class GenerationResponse(BaseModel):
    image_base64: str
    seed_used: int
    latency_seconds: float

print('[1/3] Loading ControlNet scribble model...')
controlnet = ControlNetModel.from_pretrained(
    'lllyasviel/sd-controlnet-scribble',
    torch_dtype=DTYPE
)

print('[2/3] Loading ControlNet SD pipeline (Realistic Vision V5.1)...')
cn_pipe = StableDiffusionControlNetPipeline.from_pretrained(
    'SG161222/Realistic_Vision_V5.1_noVAE',
    controlnet=controlnet,
    torch_dtype=DTYPE,
    safety_checker=None,
    requires_safety_checker=False
)
cn_pipe.scheduler = UniPCMultistepScheduler.from_config(cn_pipe.scheduler.config)
cn_pipe = cn_pipe.to(DEVICE)

print('[3/3] Loading Text-to-Image pipeline (Realistic Vision V5.1)...')
txt_pipe = StableDiffusionPipeline.from_pretrained(
    'SG161222/Realistic_Vision_V5.1_noVAE',
    torch_dtype=DTYPE,
    safety_checker=None,
    requires_safety_checker=False
)
txt_pipe.scheduler = UniPCMultistepScheduler.from_config(txt_pipe.scheduler.config)
txt_pipe = txt_pipe.to(DEVICE)
print('All models loaded!')

def b64_to_img(b64):
    if ',' in b64: b64 = b64.split(',', 1)[1]
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB').resize((512, 512))

def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

def get_gen(seed):
    g = torch.Generator(device=DEVICE)
    if seed == -1:
        seed = int(torch.randint(0, 2**32 - 1, (1,)).item())
    g.manual_seed(seed)
    return g, seed

app = FastAPI(title='Archivision T4 Engine')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], allow_methods=['*'], allow_headers=['*']
)

@app.get('/')
def root():
    return {'status': 'online', 'message': 'Archivision T4 Engine is running! Paste this URL in Archivision Studio settings.'}

@app.get('/health')
def health():
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'
    return {'status': 'healthy', 'gpu': gpu, 'models_loaded': True}

@app.post('/generate_sketch', response_model=GenerationResponse)
async def gen_sketch(req: SketchRequest):
    import asyncio
    sketch = b64_to_img(req.sketch_base64)
    gen, seed = get_gen(req.seed)
    t0 = time.perf_counter()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: cn_pipe(
        prompt=req.positive_prompt,
        negative_prompt=req.negative_prompt,
        image=sketch,
        generator=gen,
        num_inference_steps=req.num_inference_steps,
        guidance_scale=req.guidance_scale,
        controlnet_conditioning_scale=req.controlnet_conditioning_scale,
        height=512, width=512
    ))
    return GenerationResponse(
        image_base64=img_to_b64(result.images[0]),
        seed_used=seed,
        latency_seconds=round(time.perf_counter() - t0, 3)
    )

@app.post('/generate_text', response_model=GenerationResponse)
async def gen_text(req: TextRequest):
    import asyncio
    gen, seed = get_gen(req.seed)
    t0 = time.perf_counter()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: txt_pipe(
        prompt=req.positive_prompt,
        negative_prompt=req.negative_prompt,
        generator=gen,
        num_inference_steps=req.num_inference_steps,
        guidance_scale=req.guidance_scale,
        height=512, width=512
    ))
    return GenerationResponse(
        image_base64=img_to_b64(result.images[0]),
        seed_used=seed,
        latency_seconds=round(time.perf_counter() - t0, 3)
    )

# ── Start ngrok tunnel
if NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)

tunnel = ngrok.connect(PORT)
PUBLIC_URL = tunnel.public_url

print()
print('=' * 55)
print('  ARCHIVISION T4 ENGINE - ONLINE')
print(f'  PUBLIC URL: {PUBLIC_URL}')
print('  COPY this URL into GPU Tunnel box in the app')
print('=' * 55)

# Start uvicorn server in background thread
server_thread = threading.Thread(
    target=uvicorn.run, args=(app,),
    kwargs={'host': '0.0.0.0', 'port': PORT}, daemon=True
)
server_thread.start()
print(f'Server running on port {PORT}. Keep this cell alive.')

while server_thread.is_alive():
    time.sleep(30)
'''

def make_code_cell(cell_id, source_str):
    lines = source_str.split('\n')
    source_list = [line + '\n' for line in lines[:-1]] + [lines[-1]]
    return {
        "cell_type": "code",
        "metadata": {"id": cell_id},
        "source": source_list,
        "outputs": [],
        "execution_count": None
    }

cells = [
    make_code_cell("cell_install", """\
# Cell 1 — Install dependencies
!pip install -q diffusers transformers accelerate controlnet_aux pyngrok fastapi "uvicorn[standard]" torch torchvision pillow python-multipart
print('✅ Dependencies installed! Now: Runtime -> Restart session, then run Cell 2, 3, 4')\
"""),
    make_code_cell("cell_gpu", """\
# Cell 2 — Verify GPU
import torch
print('PyTorch version :', torch.__version__)
print('CUDA Available  :', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU Device      :', torch.cuda.get_device_name(0))
    print('VRAM            :', round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1), 'GB')
else:
    raise RuntimeError('No GPU detected! Set Runtime -> Change runtime type -> T4 GPU')\
"""),
    make_code_cell("cell_token", """\
# Cell 3 — Set ngrok auth token
NGROK_AUTH_TOKEN = "PASTE_YOUR_NGROK_TOKEN_HERE"
print('Auth token set!')\
"""),
    make_code_cell("cell_server", CELL4_CODE.strip()),
]

notebook = {
    "nbformat": 4,
    "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"}
    },
    "cells": cells
}

output_path = r"C:\Users\Pawan\.gemini\antigravity\scratch\archivision-studio\cloud_inference\archivision_t4_engine.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Written: {output_path}")
