import httpx
import asyncio
import base64
import time
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import io
from app.config import settings
from app.services.cv_preprocessor import base64_to_numpy, numpy_to_base64

async def _post_to_tunnel(endpoint: str, payload: dict) -> dict:
    url = f"{settings.COLAB_TUNNEL_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Tunnel request failed: {e}")

async def generate_via_sketch(sketch_b64: str, positive_prompt: str, negative_prompt: str,
                               seed: int, num_steps: int, guidance_scale: float,
                               controlnet_scale: float) -> dict:
    """
    If settings.COLAB_TUNNEL_URL is set, POST to {url}/generate_sketch.
    Otherwise, run local fallback: generate a placeholder architectural image
    that visually mimics the sketch's edge structure. Return same format:
    {image_base64: str, seed_used: int, latency_seconds: float}
    """
    if settings.COLAB_TUNNEL_URL:
        payload = {
            "sketch_base64": sketch_b64,
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
            "controlnet_conditioning_scale": controlnet_scale,
        }
        return await _post_to_tunnel("/generate_sketch", payload)
    
    # Local fallback
    start_time = time.time()
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Process sketch
    sketch_img = Image.open(io.BytesIO(base64.b64decode(sketch_b64.split(",")[-1] if "," in sketch_b64 else sketch_b64)))
    sketch_img = sketch_img.convert("RGB").resize((512, 512))
    
    # Create architectural placeholder (sepia tone overlay)
    sepia = Image.new("RGB", (512, 512), (210, 180, 140))
    blended = Image.blend(sketch_img, sepia, alpha=0.5)
    
    # Add some blur
    blended = blended.filter(ImageFilter.GaussianBlur(1))
    
    # Add text label
    draw = ImageDraw.Draw(blended)
    draw.text((20, 20), "LOCAL FALLBACK: SKETCH", fill=(0, 0, 0))
    draw.text((20, 40), f"Seed: {seed}", fill=(0, 0, 0))
    
    buffered = io.BytesIO()
    blended.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    latency = time.time() - start_time
    
    return {
        "image_base64": f"data:image/png;base64,{img_str}",
        "seed_used": seed,
        "latency_seconds": latency
    }

async def generate_via_text(positive_prompt: str, negative_prompt: str,
                             seed: int, num_steps: int, guidance_scale: float) -> dict:
    """
    If settings.COLAB_TUNNEL_URL is set, POST to {url}/generate_text.
    Otherwise, run local fallback: generate a gradient architectural placeholder.
    """
    if settings.COLAB_TUNNEL_URL:
        payload = {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
        }
        return await _post_to_tunnel("/generate_text", payload)
    
    # Local fallback
    start_time = time.time()
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Create gradient placeholder
    img = Image.new("RGB", (512, 512), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(512):
        r = int(50 + (200 * y / 512))
        g = int(50 + (100 * y / 512))
        b = 50
        draw.line([(0, y), (512, y)], fill=(r, g, b))
        
    draw.text((20, 20), "LOCAL FALLBACK: TEXT", fill=(255, 255, 255))
    draw.text((20, 40), f"Prompt: {positive_prompt[:30]}...", fill=(255, 255, 255))
    draw.text((20, 60), f"Seed: {seed}", fill=(255, 255, 255))
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    latency = time.time() - start_time
    
    return {
        "image_base64": f"data:image/png;base64,{img_str}",
        "seed_used": seed,
        "latency_seconds": latency
    }

async def check_tunnel_health() -> dict:
    """Check if tunnel URL is set and healthy. Return {connected: bool, url: str}"""
    if not settings.COLAB_TUNNEL_URL:
        return {"connected": False, "url": ""}
        
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.COLAB_TUNNEL_URL}/health")
            return {"connected": response.status_code == 200, "url": settings.COLAB_TUNNEL_URL}
    except Exception:
        return {"connected": False, "url": settings.COLAB_TUNNEL_URL}

def update_tunnel_url(new_url: str):
    """Dynamically update the tunnel URL at runtime"""
    settings.COLAB_TUNNEL_URL = new_url.rstrip('/')
