import pytest
from datetime import datetime
from app.services.parser.schemas import RawMessage
from app.services.preprocessing.cleaner import MessageCleaner

def test_basic_cleaning():
    cleaner = MessageCleaner()
    raw = RawMessage(timestamp=datetime.now(), sender="User 1", content="   Hello!   How are you?   ")
    processed = cleaner.process_message(1, raw)
    assert processed.base_clean == "Hello! How are you?"
    assert processed.metadata.word_count == 4

def test_emoji_extraction():
    cleaner = MessageCleaner()
    raw = RawMessage(timestamp=datetime.now(), sender="User 1", content="Love this! 😍✨🚀")
    processed = cleaner.process_message(1, raw)
    assert processed.metadata.emoji_count == 3
    assert "😍" in processed.metadata.emoji_list
    assert "✨" in processed.metadata.emoji_list

def test_intensity_signals():
    cleaner = MessageCleaner()
    raw = RawMessage(timestamp=datetime.now(), sender="User 2", content="WHAT IS GOING ON?!?!")
    processed = cleaner.process_message(1, raw)
    assert processed.metadata.caps_ratio > 0.8
    assert processed.metadata.repeated_punctuation_count > 0

def test_topic_variant():
    cleaner = MessageCleaner()
    # Topic variant should be lowercase, no emojis, stripped punctuation
    raw = RawMessage(timestamp=datetime.now(), sender="User 1", content="Check this: https://example.com/foo AND 🚀!")
    processed = cleaner.process_message(1, raw)
    
    topic_v = processed.variants["topic"]
    assert "🚀" not in topic_v
    assert "http" not in topic_v
    assert "and" in topic_v
    assert "check" in topic_v
    assert ":" not in topic_v

def test_repeated_chars():
    cleaner = MessageCleaner()
    raw = RawMessage(timestamp=datetime.now(), sender="User 2", content="Looooooooooooool that is so coooooool!!!")
    processed = cleaner.process_message(1, raw)
    assert processed.metadata.repeated_char_count >= 2
    assert processed.metadata.repeated_punctuation_count >= 1

def test_process_sequence():
    cleaner = MessageCleaner()
    messages = [
        RawMessage(timestamp=datetime.now(), sender="Alice", content="Hi! 👋"),
        RawMessage(timestamp=datetime.now(), sender="Bob", content="Hello Alice."),
        RawMessage(timestamp=datetime.now(), sender="Alice", content="Check this link out: https://cool.com")
    ]
    result = cleaner.process_sequence(messages)
    assert len(result.messages) == 3
    assert "Alice" in result.global_metadata["participant_stats"]
    assert "Bob" in result.global_metadata["participant_stats"]
    assert result.global_metadata["total_emojis"]["👋"] == 1
