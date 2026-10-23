"""Regenerate the Colab notebook with pip install cell included."""
import json

NGROK_TOKEN_PLACEHOLDER = "PASTE_YOUR_NGROK_TOKEN_HERE"

cells = [
    # Cell 1 — pip install ALL dependencies
    {
        "cell_type": "code",
        "metadata": {"id": "cell_install"},
        "source": [
            "# Cell 1 — Install all dependencies (run this first, ~3 min)\n",
            "# Step 1: Pin numpy first to avoid binary incompatibility\n",
            "!pip install -q 'numpy<2.0' --force-reinstall\n",
            "# Step 2: Install all required packages with compatible versions\n",
            "!pip install -q 'huggingface_hub==0.20.3' 'diffusers==0.25.1' 'transformers==4.36.2' accelerate pyngrok fastapi 'uvicorn[standard]' python-multipart pillow\n",
            "!pip install -q xformers --index-url https://download.pytorch.org/whl/cu118\n",
            "print('Done! Now go to Runtime > Restart session, then Run All again.')"
        ],
        "outputs": [],
        "execution_count": None
    },
    # Cell 2 — Check GPU
    {
        "cell_type": "code",
        "metadata": {"id": "cell_gpu_check"},
        "source": [
            "# Cell 2 — Verify T4 GPU is available\n",
            "import torch\n",
            "print('CUDA available:', torch.cuda.is_available())\n",
            "if torch.cuda.is_available():\n",
            "    print('GPU:', torch.cuda.get_device_name(0))\n",
            "    print('VRAM:', round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1), 'GB')\n",
            "else:\n",
            "    print('WARNING: No GPU detected! Go to Runtime > Change runtime type > T4 GPU')"
        ],
        "outputs": [],
        "execution_count": None
    },
    # Cell 3 — Upload colab_script.py OR write inline
    {
        "cell_type": "code",
        "metadata": {"id": "cell_write_script"},
        "source": [
            "# Cell 3 — Write the inference server script\n",
            "script = '''\n",
            "import os, time, base64, asyncio, io, threading\n",
            "from contextlib import asynccontextmanager\n",
            "from typing import Optional\n",
            "import torch\n",
            "from PIL import Image\n",
            "import uvicorn\n",
            "from fastapi import FastAPI, HTTPException\n",
            "from fastapi.middleware.cors import CORSMiddleware\n",
            "from pydantic import BaseModel\n",
            "from pyngrok import ngrok\n",
            "from diffusers import StableDiffusionPipeline, StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler\n",
            "\n",
            "NGROK_AUTH_TOKEN = os.environ.get(\"NGROK_AUTH_TOKEN\", \"\")\n",
            "PORT = 8787\n",
            "DEVICE = \"cuda\" if torch.cuda.is_available() else \"cpu\"\n",
            "DTYPE = torch.float16 if DEVICE == \"cuda\" else torch.float32\n",
            "SD_MODEL_ID = \"runwayml/stable-diffusion-v1-5\"\n",
            "CONTROLNET_MODEL_ID = \"lllyasviel/sd-controlnet-scribble\"\n",
            "\n",
            "controlnet_pipe = None\n",
            "text_pipe = None\n",
            "_models_loaded = False\n",
            "\n",
            "class SketchRequest(BaseModel):\n",
            "    sketch_base64: str\n",
            "    positive_prompt: str\n",
            "    negative_prompt: str = \"\"\n",
            "    seed: int = -1\n",
            "    num_inference_steps: int = 30\n",
            "    guidance_scale: float = 7.5\n",
            "    controlnet_conditioning_scale: float = 0.8\n",
            "\n",
            "class TextRequest(BaseModel):\n",
            "    positive_prompt: str\n",
            "    negative_prompt: str = \"\"\n",
            "    seed: int = -1\n",
            "    num_inference_steps: int = 30\n",
            "    guidance_scale: float = 7.5\n",
            "\n",
            "class GenerationResponse(BaseModel):\n",
            "    image_base64: str\n",
            "    seed_used: int\n",
            "    latency_seconds: float\n",
            "\n",
            "def load_models():\n",
            "    global controlnet_pipe, text_pipe, _models_loaded\n",
            "    print(\"Loading ControlNet...\")\n",
            "    controlnet = ControlNetModel.from_pretrained(CONTROLNET_MODEL_ID, torch_dtype=DTYPE)\n",
            "    controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(\n",
            "        SD_MODEL_ID, controlnet=controlnet, torch_dtype=DTYPE, safety_checker=None, requires_safety_checker=False)\n",
            "    controlnet_pipe.scheduler = UniPCMultistepScheduler.from_config(controlnet_pipe.scheduler.config)\n",
            "    try: controlnet_pipe.enable_xformers_memory_efficient_attention()\n",
            "    except: pass\n",
            "    controlnet_pipe = controlnet_pipe.to(DEVICE)\n",
            "    print(\"Loading Text-to-Image pipeline...\")\n",
            "    text_pipe = StableDiffusionPipeline.from_pretrained(\n",
            "        SD_MODEL_ID, torch_dtype=DTYPE, safety_checker=None, requires_safety_checker=False)\n",
            "    text_pipe.scheduler = UniPCMultistepScheduler.from_config(text_pipe.scheduler.config)\n",
            "    try: text_pipe.enable_xformers_memory_efficient_attention()\n",
            "    except: pass\n",
            "    text_pipe = text_pipe.to(DEVICE)\n",
            "    _models_loaded = True\n",
            "    print(\"All models loaded!\")\n",
            "\n",
            "def decode_b64(b64):\n",
            "    if \",\" in b64: b64 = b64.split(\",\", 1)[1]\n",
            "    return Image.open(io.BytesIO(base64.b64decode(b64))).convert(\"RGB\").resize((512,512))\n",
            "\n",
            "def encode_img(img):\n",
            "    buf = io.BytesIO()\n",
            "    img.save(buf, format=\"PNG\")\n",
            "    return base64.b64encode(buf.getvalue()).decode()\n",
            "\n",
            "def get_gen(seed):\n",
            "    g = torch.Generator(device=DEVICE)\n",
            "    if seed == -1 or seed is None: seed = int(torch.randint(0, 2**32-1, (1,)).item())\n",
            "    g.manual_seed(seed)\n",
            "    return g, seed\n",
            "\n",
            "app = FastAPI(title=\"Archivision T4 Engine\")\n",
            "app.add_middleware(CORSMiddleware, allow_origins=[\"*\"], allow_methods=[\"*\"], allow_headers=[\"*\"])\n",
            "\n",
            "@app.get(\"/health\")\n",
            "def health():\n",
            "    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"\n",
            "    return {\"status\": \"healthy\", \"gpu\": gpu, \"models_loaded\": _models_loaded}\n",
            "\n",
            "@app.post(\"/generate_sketch\", response_model=GenerationResponse)\n",
            "async def gen_sketch(req: SketchRequest):\n",
            "    if not _models_loaded: raise HTTPException(503, \"Models loading...\")\n",
            "    sketch = decode_b64(req.sketch_base64)\n",
            "    gen, seed = get_gen(req.seed)\n",
            "    t0 = time.perf_counter()\n",
            "    loop = asyncio.get_event_loop()\n",
            "    result = await loop.run_in_executor(None, lambda: controlnet_pipe(\n",
            "        prompt=req.positive_prompt, negative_prompt=req.negative_prompt,\n",
            "        image=sketch, generator=gen,\n",
            "        num_inference_steps=req.num_inference_steps,\n",
            "        guidance_scale=req.guidance_scale,\n",
            "        controlnet_conditioning_scale=req.controlnet_conditioning_scale,\n",
            "        height=512, width=512))\n",
            "    return GenerationResponse(image_base64=encode_img(result.images[0]), seed_used=seed, latency_seconds=round(time.perf_counter()-t0,3))\n",
            "\n",
            "@app.post(\"/generate_text\", response_model=GenerationResponse)\n",
            "async def gen_text(req: TextRequest):\n",
            "    if not _models_loaded: raise HTTPException(503, \"Models loading...\")\n",
            "    gen, seed = get_gen(req.seed)\n",
            "    t0 = time.perf_counter()\n",
            "    loop = asyncio.get_event_loop()\n",
            "    result = await loop.run_in_executor(None, lambda: text_pipe(\n",
            "        prompt=req.positive_prompt, negative_prompt=req.negative_prompt,\n",
            "        generator=gen, num_inference_steps=req.num_inference_steps,\n",
            "        guidance_scale=req.guidance_scale, height=512, width=512))\n",
            "    return GenerationResponse(image_base64=encode_img(result.images[0]), seed_used=seed, latency_seconds=round(time.perf_counter()-t0,3))\n",
            "'''\n",
            "\n",
            "with open('archivision_server.py', 'w') as f:\n",
            "    f.write(script)\n",
            "print('Server script written!')"
        ],
        "outputs": [],
        "execution_count": None
    },
    # Cell 4 — ngrok token
    {
        "cell_type": "code",
        "metadata": {"id": "cell_ngrok_token"},
        "source": [
            "# Cell 4 — PASTE YOUR NGROK TOKEN HERE\n",
            "import os\n",
            f"NGROK_AUTH_TOKEN = \"{NGROK_TOKEN_PLACEHOLDER}\"\n",
            "os.environ['NGROK_AUTH_TOKEN'] = NGROK_AUTH_TOKEN\n",
            "print('Token set!')"
        ],
        "outputs": [],
        "execution_count": None
    },
    # Cell 5 — Load models + start server
    {
        "cell_type": "code",
        "metadata": {"id": "cell_run_server"},
        "source": [
            "# Cell 5 — Load models and start server (takes ~3 min)\n",
            "import threading, time, os\n",
            "from pyngrok import ngrok\n",
            "import uvicorn\n",
            "\n",
            "# Import server\n",
            "exec(open('archivision_server.py').read())\n",
            "\n",
            "# Load models\n",
            "load_models()\n",
            "\n",
            "# Start ngrok tunnel\n",
            "ngrok.set_auth_token(os.environ['NGROK_AUTH_TOKEN'])\n",
            "tunnel = ngrok.connect(8787)\n",
            "PUBLIC_URL = tunnel.public_url\n",
            "\n",
            "print()\n",
            "print('=' * 55)\n",
            "print('  ARCHIVISION T4 ENGINE - ONLINE')\n",
            "print(f'  PUBLIC URL: {PUBLIC_URL}')\n",
            "print('  >>> COPY THIS URL into the GPU Tunnel box in the app')\n",
            "print('=' * 55)\n",
            "\n",
            "# Start uvicorn in background thread\n",
            "server_thread = threading.Thread(target=uvicorn.run, args=(app,), kwargs={'host':'0.0.0.0','port':8787}, daemon=True)\n",
            "server_thread.start()\n",
            "print('Uvicorn server started on port 8787')\n",
            "print('Keep this cell running...')\n",
            "\n",
            "# Keep cell alive\n",
            "while server_thread.is_alive():\n",
            "    time.sleep(30)"
        ],
        "outputs": [],
        "execution_count": None
    }
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
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print(f"Notebook written to: {output_path}")
print("Cells included:")
for i, c in enumerate(cells, 1):
    first_line = c['source'][0].strip()
    print(f"  Cell {i}: {first_line[:60]}")
