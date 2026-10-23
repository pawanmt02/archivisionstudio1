from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class RenderRequest(BaseModel):
    project_id: int
    generation_mode: Literal['sketch', 'text']
    positive_prompt: str
    negative_prompt: str = ''
    style_preset: str = 'Photorealistic'
    seed: Optional[int] = None
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    controlnet_conditioning_scale: float = 0.8
    sketch_b64: Optional[str] = None

class RenderResponse(BaseModel):
    id: int
    project_id: int
    generation_mode: str
    prompt_or_style: str
    rendered_image_b64: Optional[str]
    sketch_image_b64: Optional[str]
    edge_overlay_b64: Optional[str]
    inference_latency_seconds: Optional[float]
    edge_similarity_score: Optional[float]
    seed_used: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TunnelConfig(BaseModel):
    colab_url: str

class TunnelStatus(BaseModel):
    connected: bool
    url: str
