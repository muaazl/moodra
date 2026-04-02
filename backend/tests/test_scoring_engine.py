import pytest
from app.services.scoring.scoring_engine import ScoringEngine
from app.services.nlp.schemas import (
    SpeakerDetectionResult, ParticipantProfile, SentimentAnalysisResponse,
    MessageSentiment, ToxicityAnalysisResponse, MessageToxicity,
    TonalityAnalysisResponse, MessageTonality, TopicAnalysisResponse,
    TopicSegment, ParticipantSentiment, ParticipantToxicity, ParticipantTonality,
    SentimentTrendPoint
)
from app.services.preprocessing.schemas import PreprocessingResult

@pytest.fixture
def mock_analysis_data():
    # Setup mock data for a 2-person chat
    speakers = SpeakerDetectionResult(
        participants=[
            ParticipantProfile(name="Alice", messages_sent=10, words_total=100, dominance_score=0.6),
            ParticipantProfile(name="Bob", messages_sent=5, words_total=30, dominance_score=0.4)
        ]
    )
    
    sentiment = SentimentAnalysisResponse(
        messages=[
            MessageSentiment(message_id=i, sender="Alice", score=0.5, label="positive", confidence=0.9)
            for i in range(10)
        ] + [
            MessageSentiment(message_id=i+10, sender="Bob", score=-0.2, label="negative", confidence=0.8)
            for i in range(5)
        ],
        participants=[
            ParticipantSentiment(name="Alice", overall_score=0.5, pos_count=10, neg_count=0, neutral_count=0),
            ParticipantSentiment(name="Bob", overall_score=-0.2, pos_count=0, neg_count=5, neutral_count=0)
        ],
        timeline=[
            SentimentTrendPoint(label="10:00", average_score=0.5, smoothed_score=0.5, volume=10),
            SentimentTrendPoint(label="10:05", average_score=-0.2, smoothed_score=-0.2, volume=5)
        ],
        summary_metrics={
            "overall_sentiment": "positive",
            "positivity_rate": 0.67,
            "negativity_rate": 0.33,
            "volatility": 0.1
        }
    )
    
    toxicity = ToxicityAnalysisResponse(
        messages=[
            MessageToxicity(message_id=i, score=0.1, label="low", confidence=0.9)
            for i in range(15)
        ],
        participants=[
            ParticipantToxicity(name="Alice", intensity_index=0.1, outburst_count=0, max_heat=0.1),
            ParticipantToxicity(name="Bob", intensity_index=0.1, outburst_count=0, max_heat=0.1)
        ],
        global_intensity=0.1
    )
    
    tonality = TonalityAnalysisResponse(
        messages=[
            MessageTonality(message_id=i, dryness_score=0.2, passive_aggression_score=0.1, confidence=0.8)
            for i in range(15)
        ],
        participants=[
            ParticipantTonality(name="Alice", avg_dryness=0.2, avg_passive_aggression=0.1),
            ParticipantTonality(name="Bob", avg_dryness=0.5, avg_passive_aggression=0.4)
        ]
    )
    
    topics = TopicAnalysisResponse(
        segments=[
            TopicSegment(id=1, start_id=0, end_id=9, label="Greetings", confidence=0.9, message_count=10, sentiment_avg=0.5),
            TopicSegment(id=2, start_id=10, end_id=14, label="The Problem", confidence=0.8, message_count=5, sentiment_avg=-0.2)
        ],
        clusters=[],
        shifts=[10]
    )
    
    preprocessed = PreprocessingResult(messages=[]) # Minimal for this test
    
    return preprocessed, speakers, sentiment, toxicity, tonality, topics

def test_scoring_engine_flow(mock_analysis_data):
    engine = ScoringEngine()
    result = engine.analyze(*mock_analysis_data)
    
    assert result.overall_mood == "Wholesome & Energetic"
    assert len(result.participants) == 2
    
    alice = next(p for p in result.participants if p.name == "Alice")
    bob = next(p for p in result.participants if p.name == "Bob")
    
    # Alice should be more dominant
    assert alice.dominance.value > bob.dominance.value
    assert "The Driver" in alice.badges
    
    # Bob should be drier
    assert bob.dry_texting.value > alice.dry_texting.value
    
    # Check segments
    assert len(result.segments) == 2
    assert result.segments[0].topic_label == "Greetings"
    assert result.segments[1].topic_label == "The Problem"
    
    # Check standout cards
    assert len(result.standout_cards) > 0
    print(f"\nResulting Summary: {result.overall_summary}")
    for card in result.standout_cards:
        print(f"Card: {card.title} -> {card.recipient}: {card.description}")

if __name__ == "__main__":
    # If run directly, we can see the output
    import sys
    from pydantic import BaseModel
    
    # Minimal mock objects if we don't have pytest
    # (Simplified for direct run demonstration)
    pass
