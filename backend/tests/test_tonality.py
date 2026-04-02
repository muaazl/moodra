import pytest
from datetime import datetime, timedelta
from app.services.nlp.tonality_analyzer import TonalityAnalyzer
from app.services.nlp.schemas import MessageSentiment
from app.services.parser.schemas import RawMessage

@pytest.fixture
def analyzer():
    return TonalityAnalyzer()

def test_dry_texting_signals(analyzer):
    messages = [
        RawMessage(timestamp=datetime.now(), sender="Alice", content="Hey what are you doing tonight? Do you want to grab some pizza?"),
        RawMessage(timestamp=datetime.now() + timedelta(minutes=10), sender="Bob", content="k")
    ]
    
    # Mock sentiment: Alice is positive, Bob is neutral
    sentiments = [
        MessageSentiment(message_id=0, sender="Alice", score=0.8, label="positive", confidence=0.9),
        MessageSentiment(message_id=1, sender="Bob", score=0.0, label="neutral", confidence=0.5)
    ]
    
    result = analyzer.analyze_chat(messages, sentiments)
    
    bob_msg = result.messages[1]
    assert bob_msg.dryness_score > 0.6
    assert any(s.type == "brevity" for s in bob_msg.signals)

def test_passive_aggression_signals(analyzer):
    messages = [
        RawMessage(timestamp=datetime.now(), sender="Alice", content="I forgot to buy milk, sorry!"),
        RawMessage(timestamp=datetime.now() + timedelta(minutes=5), sender="Bob", content="fine.")
    ]
    
    sentiments = [
        MessageSentiment(message_id=0, sender="Alice", score=-0.2, label="negative", confidence=0.8),
        # Bob's "fine" might be labeled positive or neutral by model, but context makes it PA
        MessageSentiment(message_id=1, sender="Bob", score=0.5, label="positive", confidence=0.5)
    ]
    
    result = analyzer.analyze_chat(messages, sentiments)
    
    bob_msg = result.messages[1]
    assert bob_msg.passive_aggression_score > 0.4
    # Check for abruptness or mismatch signals
    signal_types = [s.type for s in bob_msg.signals]
    assert "abruptness" in signal_types or "mismatch" in signal_types or "pa_phrasing" in signal_types

def test_participant_aggregation(analyzer):
    messages = [
        RawMessage(timestamp=datetime.now(), sender="DryGuy", content="ok"),
        RawMessage(timestamp=datetime.now() + timedelta(seconds=1), sender="DryGuy", content="no"),
        RawMessage(timestamp=datetime.now() + timedelta(seconds=2), sender="VibrantGal", content="Omg that is so cool!!! 🎉")
    ]
    
    sentiments = [
        MessageSentiment(message_id=0, sender="DryGuy", score=0, label="neutral", confidence=1),
        MessageSentiment(message_id=1, sender="DryGuy", score=0, label="neutral", confidence=1),
        MessageSentiment(message_id=2, sender="VibrantGal", score=0.9, label="positive", confidence=1)
    ]
    
    result = analyzer.analyze_chat(messages, sentiments)
    
    dry_guy = next(p for p in result.participants if p.name == "DryGuy")
    vibrant_gal = next(p for p in result.participants if p.name == "VibrantGal")
    
    assert dry_guy.avg_dryness > vibrant_gal.avg_dryness
    assert "brevity" in dry_guy.top_signals or "low_vibrancy" in dry_guy.top_signals
