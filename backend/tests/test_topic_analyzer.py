import pytest
from app.services.nlp.topic_analyzer import TopicAnalyzer
from app.services.preprocessing.schemas import PreprocessedMessage, MessageMetadata
from app.services.parser.schemas import RawMessage
from datetime import datetime

@pytest.fixture
def analyzer():
    return TopicAnalyzer()

def create_mock_msg(msg_id, sender, content):
    raw = RawMessage(sender=sender, content=content, timestamp=datetime.now())
    return PreprocessedMessage(
        message_id=msg_id,
        raw=raw,
        base_clean=content,
        variants={"topic": content.lower()},
        metadata=MessageMetadata(word_count=len(content.split()))
    )

def test_topic_analyzer_basic(analyzer):
    # Create sample messages with distinct topics
    messages = [
        # Topic 1: Work/Meeting
        create_mock_msg(1, "Alice", "Are we still having the meeting at 3pm?"),
        create_mock_msg(2, "Bob", "Yes, we need to discuss the project roadmap."),
        create_mock_msg(3, "Alice", "Cool, I will bring the printed documents."),
        create_mock_msg(4, "Bob", "Great, see you in the conference room."),
        create_mock_msg(5, "Alice", "Wait, which room was it again?"),
        
        # Topic 2: Dinner/Food
        create_mock_msg(6, "Bob", "By the way, what are we doing for dinner tonight?"),
        create_mock_msg(7, "Alice", "I was thinking about that new Italian place."),
        create_mock_msg(8, "Bob", "Oh, the one with the great pasta?"),
        create_mock_msg(9, "Alice", "Yeah, exactly. I'm craving some lasagna."),
        create_mock_msg(10, "Bob", "Lasagna sounds perfect. Let's book a table."),
        
        # Topic 1 again: Back to work
        create_mock_msg(11, "Alice", "Also, don't forget to send me the roadmap draft."),
        create_mock_msg(12, "Bob", "I'll email it to you before the meeting starts."),
    ]
    
    result = analyzer.analyze(messages)
    
    # We expect at least 1 or more segments
    assert len(result.segments) >= 1
    
    # We expect at least 1 cluster
    assert len(result.clusters) >= 1
    
    # Check if we extracted any reasonable keywords
    has_keywords = any(len(c.keywords) > 0 for c in result.clusters)
    assert has_keywords

def test_topic_analyzer_empty(analyzer):
    result = analyzer.analyze([])
    assert result.segments == []
    assert result.clusters == []

def test_topic_analyzer_short(analyzer):
    # Too short for windowed shift detection, should return one segment
    messages = [
        create_mock_msg(1, "Alice", "Hello"),
        create_mock_msg(2, "Bob", "Hi there"),
    ]
    result = analyzer.analyze(messages)
    assert len(result.segments) == 1
    assert len(result.clusters) == 1
