from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ScoreMetadata(BaseModel):
    """Encapsulates a score with its qualitative label and explanation."""
    value: float = Field(..., description="Normalized score from 0.0 to 1.0")
    label: str = Field(..., description="Qualitative label (e.g. 'High', 'Low', 'Intense')")
    explanation: str = Field(..., description="Probabilistic explanation of why this score was given")
    confidence: float = Field(..., description="Confidence of the underlying models (0.0 to 1.0)")

class ParticipantScoring(BaseModel):
    """High-level metrics for a single participant."""
    name: str
    dominance: ScoreMetadata
    dry_texting: ScoreMetadata
    passive_aggression: ScoreMetadata
    main_character_energy: ScoreMetadata
    gaslighting_index: ScoreMetadata
    red_flag_score: ScoreMetadata
    
    # Simple list of "badges" or "labels" for the UI
    badges: List[str] = Field(default_factory=list)

class SegmentScoring(BaseModel):
    """High-level metrics for a conversation segment."""
    segment_id: int
    topic_label: str
    tension: ScoreMetadata
    mood: str # e.g. "Wholesome", "Heated", "Dry"
    notable_message_id: Optional[int] = None
    notable_reason: Optional[str] = None

class StandoutCard(BaseModel):
    """Data for a shareable 'Achievement' or 'Red Flag' card."""
    type: str = Field(..., description="e.g. 'award', 'red_flag', 'statistic'")
    title: str
    recipient: str
    description: str
    icon_hint: str # e.g. "crown", "fire", "ice-cube"

class ScoringResponse(BaseModel):
    """The final aggregate output of the Expose The Chat engine."""
    overall_summary: str
    roast_summary: str
    overall_mood: str
    
    # Aggregated metrics
    participants: List[ParticipantScoring]
    segments: List[SegmentScoring]
    
    # Timeline points for the chart
    timeline: List[Dict[str, Any]] = Field(
        ..., 
        description="List of points with {timestamp/index, tension, sentiment, volume}"
    )
    
    # Standout observations
    standout_cards: List[StandoutCard] = Field(default_factory=list)
    
    # Global metrics
    global_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "conversation_health": 0.0,
            "most_active_hour": None,
            "total_messages": 0
        }
    )
