from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
class EntityMatch(BaseModel):
    """A single extraction of a named entity (PERSON) from chat content."""
    text: str
    label: str = "PERSON"
    start_char: int
    end_char: int
    confidence: float
    message_id: int
    context: Optional[str] = None
class ParticipantProfile(BaseModel):
    """The persona of a chat participant (either a sender or someone mentioned)."""
    name: str
    aliases: List[str] = Field(default_factory=list)
    is_sender: bool = False
    messages_sent: int = 0
    mentions: List[EntityMatch] = Field(default_factory=list)
    mention_count: int = 0
    words_total: int = 0
    dominance_score: float = 0.0
    centrality_score: float = 0.0
    sentiment_received: List[float] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
class SpeakerDetectionResult(BaseModel):
    """The result of the speaker and entity analysis."""
    participants: List[ParticipantProfile]
    unidentified_entities: List[EntityMatch] = Field(default_factory=list)
    alias_map: Dict[str, str] = Field(default_factory=dict)
    global_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "top_referenced_person": None,
            "most_dominant_speaker": None,
            "total_entities_detected": 0,
            "participant_count": 0
        }
    )
class MessageSentiment(BaseModel):
    """Sentiment results for a single message."""
    message_id: int
    sender: Optional[str] = None
    score: float = Field(..., description="Continuous score from -1.0 (negative) to 1.0 (positive)")
    label: str = Field(..., description="The classification: 'positive', 'neutral', or 'negative'")
    confidence: float = Field(..., description="Model classification confidence (0-1)")
class SentimentTrendPoint(BaseModel):
    """A data point for the sentiment timeline chart."""
    label: str
    average_score: float
    smoothed_score: float
    volume: int
class ParticipantSentiment(BaseModel):
    """Sentiment profile for a single participant."""
    name: str
    overall_score: float
    pos_count: int
    neg_count: int
    neutral_count: int
    top_emotions: Dict[str, float] = Field(default_factory=dict)
class SentimentAnalysisResponse(BaseModel):
    """The aggregate sentiment analysis results ready for frontend ingestion."""
    messages: List[MessageSentiment]
    participants: List[ParticipantSentiment]
    timeline: List[SentimentTrendPoint]
    summary_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "overall_sentiment": "neutral",
            "positivity_rate": 0.0,
            "negativity_rate": 0.0,
            "volatility": 0.0
        }
    )
class MessageToxicity(BaseModel):
    """Toxicity results for a single message."""
    message_id: int
    sender: Optional[str] = None
    score: float = Field(..., description="Intensity score from 0.0 to 1.0")
    label: str = Field(..., description="The intensity classification: 'low', 'medium', 'high'")
    confidence: float = Field(..., description="Model classification confidence (0-1)")
    top_category: Optional[str] = Field(None, description="The primary toxicity category detected")
    categories: Dict[str, float] = Field(default_factory=dict)
    is_high_risk: bool = False
class ParticipantToxicity(BaseModel):
    """Toxicity profile for a single participant."""
    name: str
    intensity_index: float
    outburst_count: int
    max_heat: float
    risky_message_ids: List[int] = Field(default_factory=list)
class ToxicityAnalysisResponse(BaseModel):
    """The aggregate toxicity analysis results."""
    messages: List[MessageToxicity]
    participants: List[ParticipantToxicity]
    global_intensity: float
    summary_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "most_intense_user": None,
            "high_risk_ratio": 0.0,
            "peak_tension_segment": None,
            "uncertainty_index": 0.0
        }
    )
class TonalitySignal(BaseModel):
    """A specific signal contributing to a tonality score (for explainability)."""
    type: str
    score_influence: float
    description: str
class MessageTonality(BaseModel):
    """Passive aggression and Dryness results for a single message."""
    message_id: int
    sender: Optional[str] = None
    dryness_score: float = Field(..., description="Continuous score from 0.0 (not dry) to 1.0 (very dry)")
    passive_aggression_score: float = Field(..., description="Continuous score from 0.0 (none) to 1.0 (highly passive-aggressive)")
    confidence: float
    signals: List[TonalitySignal] = Field(default_factory=list)
class ParticipantTonality(BaseModel):
    """Tonality profile for a single participant."""
    name: str
    avg_dryness: float
    avg_passive_aggression: float
    top_signals: List[str] = Field(default_factory=list)
    consistency_score: float = 0.0
class TonalityAnalysisResponse(BaseModel):
    """The aggregate tonality analysis results."""
    messages: List[MessageTonality]
    participants: List[ParticipantTonality]
    summary_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "overall_dryness": 0.0,
            "overall_passive_aggression": 0.0,
            "most_passive_aggressive_user": None,
            "driest_user": None,
            "tension_points": []
        }
    )
class TopicSegment(BaseModel):
    """A contiguous segment of messages that share a single topic."""
    id: int
    start_id: int
    end_id: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    label: str = Field(..., description="A short, representative label for the topic")
    summary: Optional[str] = Field(None, description="A slightly longer description of what was discussed")
    keywords: List[str] = Field(default_factory=list)
    confidence: float
    message_count: int
    sentiment_avg: Optional[float] = None
class TopicCluster(BaseModel):
    """A group of segments across the timeline that belong to the same recurring topic."""
    cluster_id: int
    label: str
    segment_ids: List[int]
    keywords: List[str]
    reoccurrence_count: int
    total_messages: int
class TopicAnalysisResponse(BaseModel):
    """The aggregate topic analysis results."""
    segments: List[TopicSegment]
    clusters: List[TopicCluster]
    shifts: List[int] = Field(..., description="Message IDs where a significant topic shift was detected")
    summary_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_topics": 0,
            "most_recurring_topic": None,
            "conversation_fluidity": 0.0,
            "dominant_topic": None
        }
    )
