from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ScoreMetadata(BaseModel):
    """Encapsulates a score with its qualitative label and explanation."""
    value: float = Field(..., description="Normalized score from 0.0 to 1.0")
    label: str = Field(..., description="Qualitative label (e.g. 'High', 'Low', 'Intense')")
    explanation: str = Field(..., description="Probabilistic explanation of why this score was given")
    confidence: float = Field(..., description="Confidence of the underlying models (0.0 to 1.0)")

class NotableQuote(BaseModel):
    """A direct quote from the participant serving as proof/receipts."""
    message_id: Optional[int]
    text: str
    context: str = Field(..., description="e.g. 'Biggest Red Flag', 'The Brick Wall'")

class ParticipantScoring(BaseModel):
    """High-level metrics for a single participant."""
    name: str
    dominance: ScoreMetadata
    effort_level: ScoreMetadata
    hidden_attitude: ScoreMetadata
    self_focus: ScoreMetadata
    manipulation_level: ScoreMetadata
    red_flag_score: ScoreMetadata
    
    # Group Attributes
    peacemaker_index: ScoreMetadata
    instigator_score: ScoreMetadata
    ghost_level: ScoreMetadata
    yap_score: ScoreMetadata
    clown_factor: ScoreMetadata
    
    # Dyad Attributes
    simp_level: ScoreMetadata
    response_effort: ScoreMetadata
    apology_rate: ScoreMetadata
    
    # Simple list of "badges" or "labels" for the UI
    badges: List[str] = Field(default_factory=list)
    
    # Memorable messages as "receipts"
    notable_quotes: List[NotableQuote] = Field(default_factory=list)

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
    """The final aggregate output of the Moodra engine."""
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
