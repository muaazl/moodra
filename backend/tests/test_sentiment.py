import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.parser.schemas import RawMessage
from app.services.nlp.sentiment_analyzer import SentimentAnalyzer

@pytest.fixture
def mock_sentiments():
    """Mock results for the transformers pipeline."""
    return [
        [
            {"label": "positive", "score": 0.9},
            {"label": "neutral", "score": 0.05},
            {"label": "negative", "score": 0.05}
        ]
    ]

def test_sentiment_analyzer_logic():
    # We mock out the actual pipeline call to test the aggregation and smoothing logic
    with patch("app.services.nlp.sentiment_analyzer.pipeline") as mock_pipeline:
        # Define mock behavior
        mock_pipe_instance = MagicMock()
        mock_pipeline.return_value = mock_pipe_instance
        
        # Return positive for "happy", negative for "sad"
        def side_effect(content):
            if "happy" in content:
                return [[{"label": "positive", "score": 0.9}, {"label": "neutral", "score": 0.05}, {"label": "negative", "score": 0.05}]]
            elif "sad" in content:
                return [[{"label": "negative", "score": 0.9}, {"label": "neutral", "score": 0.05}, {"label": "positive", "score": 0.05}]]
            else:
                return [[{"label": "neutral", "score": 0.9}, {"label": "positive", "score": 0.05}, {"label": "negative", "score": 0.05}]]
        
        mock_pipe_instance.side_effect = side_effect
        
        analyzer = SentimentAnalyzer()
        
        # Create dummy messages
        messages = [
            RawMessage(timestamp=datetime.now(), sender="Alice", content="I am so happy!"),
            RawMessage(timestamp=datetime.now(), sender="Bob", content="This is very sad."),
            RawMessage(timestamp=datetime.now(), sender="Alice", content="Just okay."),
            RawMessage(timestamp=datetime.now(), sender="Alice", content="Still happy.")
        ]
        
        response = analyzer.analyze_chat(messages)
        
        assert len(response.messages) == 4
        assert response.messages[0].label == "positive"
        assert response.messages[1].label == "negative"
        
        # Check participant aggregation
        alice_data = next(p for p in response.participants if p.name == "Alice")
        assert alice_data.pos_count == 2
        assert alice_data.neutral_count == 1
        
        # Check timeline
        assert len(response.timeline) > 0
        for point in response.timeline:
            assert hasattr(point, "smoothed_score")

def test_empty_chat():
    analyzer = SentimentAnalyzer()
    # We shouldn't even need the pipeline for an empty list if handled correctly
    response = analyzer.analyze_chat([])
    assert len(response.messages) == 0
    assert len(response.participants) == 0
    assert len(response.timeline) == 0

def test_media_omitted_handling():
    analyzer = SentimentAnalyzer()
    msg = RawMessage(timestamp=datetime.now(), sender="Alice", content="<Media omitted>", is_media=True)
    
    # Logic should skip pipeline for media
    with patch("app.services.nlp.sentiment_analyzer.SentimentAnalyzer.pipeline") as mock_pipe:
        res = analyzer.analyze_message(msg, 0)
        assert res.label == "neutral"
        assert res.score == 0.0
        assert res.confidence == 0.0
        mock_pipe.assert_not_called()
