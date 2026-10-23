from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RenderHistory(Base):
    __tablename__ = "render_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    generation_mode = Column(String(20), nullable=False)
    prompt_or_style = Column(Text)
    sketch_image_b64 = Column(Text, nullable=True)
    rendered_image_b64 = Column(Text, nullable=True)
    edge_overlay_b64 = Column(Text, nullable=True)
    inference_latency_seconds = Column(Float, nullable=True)
    edge_similarity_score = Column(Float, nullable=True)
    seed_used = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="renders")
