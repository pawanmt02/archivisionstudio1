from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectCreate(BaseModel):
    title: str
    canvas_json_state: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    canvas_json_state: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    canvas_json_state: Optional[str]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
