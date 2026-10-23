from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.render import RenderHistory
from app.schemas.render_schema import RenderRequest, RenderResponse, TunnelConfig, TunnelStatus
from app.utils.security import get_current_user
from app.services.cv_preprocessor import preprocess_sketch
from app.services.prompt_matrix import build_sketch_prompt, build_text_prompt
from app.services.colab_client import generate_via_sketch, generate_via_text, check_tunnel_health, update_tunnel_url
from app.services.evaluator import evaluate_generation

router = APIRouter(prefix="/synthesis", tags=["Synthesis"])

@router.post("/generate", response_model=RenderResponse)
async def generate_render(request: RenderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Validate request
    if request.generation_mode == 'sketch' and not request.sketch_b64:
        raise HTTPException(status_code=400, detail="Sketch is required for sketch mode")
        
    # 2. Get project
    project = db.query(Project).filter(Project.id == request.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 3. Setup seed
    seed = request.seed if request.seed is not None else random.randint(0, 2**32 - 1)
    
    cleaned_sketch = None
    edge_overlay = None
    edge_score = None
    
    try:
        if request.generation_mode == 'sketch':
            # Preprocess
            _, cleaned_sketch = preprocess_sketch(request.sketch_b64)
            
            # Prompts
            pos, neg = build_sketch_prompt(request.positive_prompt, request.style_preset)
            if request.negative_prompt:
                neg = f"{request.negative_prompt}, {neg}"
                
            # Generate
            result = await generate_via_sketch(
                sketch_b64=cleaned_sketch,
                positive_prompt=pos,
                negative_prompt=neg,
                seed=seed,
                num_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                controlnet_scale=request.controlnet_conditioning_scale
            )
            
            # Evaluate
            eval_result = evaluate_generation(cleaned_sketch, result["image_base64"])
            edge_overlay = eval_result["edge_overlay_b64"]
            edge_score = eval_result["iou_score"]
            
        else:
            # Text mode
            pos, neg = build_text_prompt(request.positive_prompt, request.style_preset)
            if request.negative_prompt:
                neg = f"{request.negative_prompt}, {neg}"
                
            result = await generate_via_text(
                positive_prompt=pos,
                negative_prompt=neg,
                seed=seed,
                num_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale
            )
            
        # Save to DB
        new_render = RenderHistory(
            project_id=project.id,
            generation_mode=request.generation_mode,
            prompt_or_style=request.positive_prompt,
            sketch_image_b64=cleaned_sketch,
            rendered_image_b64=result["image_base64"],
            edge_overlay_b64=edge_overlay,
            inference_latency_seconds=result.get("latency_seconds"),
            edge_similarity_score=edge_score,
            seed_used=result["seed_used"]
        )
        db.add(new_render)
        db.commit()
        db.refresh(new_render)
        
        return new_render
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tunnel-status", response_model=TunnelStatus)
async def get_tunnel_status():
    return await check_tunnel_health()

@router.post("/tunnel-config", response_model=TunnelStatus)
async def set_tunnel_config(config: TunnelConfig):
    update_tunnel_url(config.colab_url)
    return await check_tunnel_health()
