import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import numpy as np

from app.services.parser.schemas import RawMessage
from app.services.nlp.toxicity_analyzer import ToxicityAnalyzer

@pytest.fixture
def mock_toxicity_results():
    """Returns a factory function for generating mock pipeline results."""
    def _create_mock(label_scores: dict):
        # The pipeline returns a list of results (top_k=None means all labels included)
        return [[{"label": k, "score": v} for k, v in label_scores.items()]]
    return _create_mock

def test_toxicity_analyzer_basic_logic(mock_toxicity_results):
    """Test that the analyzer correctly maps model outputs to our schema."""
    with patch("app.services.nlp.toxicity_analyzer.pipeline") as mock_pipeline:
        mock_pipe_instance = MagicMock()
        mock_pipeline.return_value = mock_pipe_instance

        # Return high toxicity for "hate", low for "nice"
        def side_effect(content):
            if "hate" in content:
                return mock_toxicity_results({
                    "toxic": 0.95, "severe_toxic": 0.1, "obscene": 0.05, 
                    "threat": 0.01, "insult": 0.8, "identity_hate": 0.05
                })
            else:
                return mock_toxicity_results({
                    "toxic": 0.01, "severe_toxic": 0.0, "obscene": 0.0, 
                    "threat": 0.0, "insult": 0.01, "identity_hate": 0.0
                })
        
        mock_pipe_instance.side_effect = side_effect
        
        analyzer = ToxicityAnalyzer()
        
        # Test 1: High risk message
        msg_high = RawMessage(timestamp=datetime.now(), sender="Alice", content="I really hate this person.")
        res_high = analyzer.analyze_message(msg_high, 0)
        assert res_high.label == "high"
        assert res_high.score >= 0.9
        assert res_high.is_high_risk is True
        assert res_high.top_category == "toxic"

        # Test 2: Low risk message
        msg_low = RawMessage(timestamp=datetime.now(), sender="Bob", content="Hello everyone!")
        res_low = analyzer.analyze_message(msg_low, 1)
        assert res_low.label == "low"
        assert res_low.score < 0.1
        assert res_low.is_high_risk is False

def test_analyze_chat_aggregation(mock_toxicity_results):
    """Test that the analyzer correctly aggregates results per participant and globally."""
    with patch("app.services.nlp.toxicity_analyzer.pipeline") as mock_pipeline:
        mock_pipe_instance = MagicMock()
        mock_pipeline.return_value = mock_pipe_instance

        # Alice: 1 toxic, 1 clean
        # Bob: 1 neutral-ish
        def side_effect(content):
            if "bad" in content:
                return mock_toxicity_results({"toxic": 0.9, "insult": 0.8})
            elif "mean" in content:
                return mock_toxicity_results({"toxic": 0.6, "insult": 0.4})
            else:
                return mock_toxicity_results({"toxic": 0.05})
        
        mock_pipe_instance.side_effect = side_effect
        
        analyzer = ToxicityAnalyzer()
        
        messages = [
            RawMessage(timestamp=datetime.now(), sender="Alice", content="This is bad"),
            RawMessage(timestamp=datetime.now(), sender="Bob", content="This is mean"),
            RawMessage(timestamp=datetime.now(), sender="Alice", content="This is good")
        ]
        
        response = analyzer.analyze_chat(messages)
        
        assert len(response.messages) == 3
        assert len(response.participants) == 2
        
        alice = next(p for p in response.participants if p.name == "Alice")
        bob = next(p for p in response.participants if p.name == "Bob")
        
        assert alice.outburst_count == 1
        assert alice.risky_message_ids == [0] # ID of "This is bad"
        assert bob.outburst_count == 1 # Since 0.5 > 0.4 (threshold is 0.5 in code)
        
        # Check global summary
        assert response.summary_metrics["most_intense_user"] in ["Alice", "Bob"]
        assert response.summary_metrics["high_risk_ratio"] == round(2/3, 3)

def test_edge_cases():
    """Test empty chats and media handling."""
    analyzer = ToxicityAnalyzer()
    
    # Empty chat
    response = analyzer.analyze_chat([])
    assert response.global_intensity == 0.0
    assert len(response.messages) == 0
    
    # Media handling
    msg_media = RawMessage(timestamp=datetime.now(), sender="Alice", content="<Media omitted>", is_media=True)
    res_media = analyzer.analyze_message(msg_media, 0)
    assert res_media.label == "low"
    assert res_media.score == 0.0
    assert res_media.is_high_risk is False
