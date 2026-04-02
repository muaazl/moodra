import pytest
from datetime import datetime
from app.services.nlp.entity_extractor import EntityExtractor
from app.services.preprocessing.schemas import PreprocessingResult, PreprocessedMessage, MessageMetadata
from app.services.parser.schemas import RawMessage

@pytest.fixture
def sample_preprocessed_data():
    """Create mock preprocessed chat data for testing."""
    messages = [
        PreprocessedMessage(
            message_id=1,
            raw=RawMessage(timestamp=datetime.now(), sender="Alice Walker", content="Hey Bob, did you see Charlie today?"),
            base_clean="Hey Bob, did you see Charlie today?",
            variants={"speaker": "Hey Bob, did you see Charlie today?"},
            metadata=MessageMetadata(word_count=7)
        ),
        PreprocessedMessage(
            message_id=2,
            raw=RawMessage(timestamp=datetime.now(), sender="Bob Builder", content="No Alice, I haven't seen Charlie."),
            base_clean="No Alice, I haven't seen Charlie.",
            variants={"speaker": "No Alice, I haven't seen Charlie."},
            metadata=MessageMetadata(word_count=6)
        ),
        PreprocessedMessage(
            message_id=3,
            raw=RawMessage(timestamp=datetime.now(), sender="Alice Walker", content="Okay, thanks Bob."),
            base_clean="Okay, thanks Bob.",
            variants={"speaker": "Okay, thanks Bob."},
            metadata=MessageMetadata(word_count=3)
        )
    ]
    return PreprocessingResult(messages=messages)

def test_entity_extraction_and_resolution(sample_preprocessed_data):
    """Test that NER extracts names and associates first names to full name senders."""
    extractor = EntityExtractor(model_name="en_core_web_md")
    result = extractor.analyze_speakers(sample_preprocessed_data)
    
    # Alice Walker (Sender) should be matched with "Alice" mention
    alice_profile = next(p for p in result.participants if p.name == "Alice Walker")
    assert alice_profile.is_sender is True
    assert alice_profile.messages_sent == 2
    # spaCy should catch "Alice" in the second message. 
    # Even if spaCy misses it in this tiny sample, our logic should handle if it catches it.
    
    # Bob Builder (Sender) should be matched with "Bob" mention
    bob_profile = next(p for p in result.participants if p.name == "Bob Builder")
    assert bob_profile.is_sender is True
    assert bob_profile.messages_sent == 1
    
    # Charlie should be a mentioned-only participant
    charlie_profile = next((p for p in result.participants if "Charlie" in p.name), None)
    assert charlie_profile is not None
    assert charlie_profile.is_sender is False
    assert charlie_profile.mention_count >= 1
    
    # Check centrality
    # Bob was mentioned by Alice (Walker). Alice was mentioned by Bob (Builder).
    # Since there are 2 senders, max centrality is 1.0.
    assert alice_profile.centrality_score > 0
    assert bob_profile.centrality_score > 0
    
    print(f"Global Metrics: {result.global_metrics}")
    for p in result.participants:
        print(f"Profile: {p.name} | S: {p.is_sender} | M: {p.mention_count} | D: {p.dominance_score:.2f} | C: {p.centrality_score:.2f}")

if __name__ == "__main__":
    # Ensure spacy model is downloaded before running manually
    import subprocess
    import sys
    try:
        import spacy
        spacy.load("en_core_web_md")
    except:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        
    data = sample_preprocessed_data()
    test_entity_extraction_and_resolution(data)
