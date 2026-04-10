from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from ..services.scoring.schemas import ScoringResponse
class AnalysisRequest(BaseModel):
    """Request for text-based analysis."""
    text: str = Field(..., min_length=10, description="The raw chat export or pasted text.")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom analysis flags.")
class AnalysisSuccessResponse(BaseModel):
    """Standard success response wrapper."""
    status: str = "success"
    data: ScoringResponse
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": None,
            "processing_time": 0.0
        }
    )
class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    status: str = "error"
    code: str = "ANALYSIS_FAILED"
    message: str
    details: Optional[Dict[str, Any]] = None
