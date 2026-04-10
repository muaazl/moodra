import re
import emoji
from typing import List, Dict, Tuple, Any, Optional
import pandas as pd
import numpy as np
import spacy
from ..parser.schemas import RawMessage
from .schemas import PreprocessedMessage, MessageMetadata, PreprocessingResult
from .constants import (
    URL_PATTERN, 
    REPEATED_PUNCTUATION_PATTERN, 
    REPEATED_CHARACTER_PATTERN, 
    WHITESPACE_PATTERN,
    PUNCTUATION_REMOVAL_PATTERN
)
class MessageCleaner:
    """Preprocesses raw chat messages into analysis-ready formats."""
    def __init__(self, model_name: str = "en_core_web_sm", nlp: Optional[spacy.language.Language] = None):
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load(model_name)
            except OSError:
                self.nlp = None
    def _is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji using the emoji library."""
        return emoji.is_emoji(char)
    def extract_emojis(self, text: str) -> List[str]:
        """Extract all emojis from a string."""
        return [char for char in text if self._is_emoji(char)]
    def get_caps_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase letters to total letters."""
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0.0
        return sum(1 for c in letters if c.isupper()) / len(letters)
    def count_repeated_patterns(self, text: str, pattern: re.Pattern) -> int:
        """Count matches for a specific regex pattern."""
        return len(pattern.findall(text))
    def clean_base(self, text: str) -> str:
        """Standard cleaning: trimming and workspace normalization."""
        text = text.strip()
        text = WHITESPACE_PATTERN.sub(" ", text)
        return text
    def generate_variants(self, text: str, emojis: List[str]) -> Dict[str, str]:
        """Generate specific cleaned versions of the text for different ML tasks."""
        base = self.clean_base(text)
        sentiment_v = URL_PATTERN.sub("[URL]", base)
        topic_v = "".join([c for c in base if not self._is_emoji(c)])
        topic_v = URL_PATTERN.sub("", topic_v)
        topic_v = PUNCTUATION_REMOVAL_PATTERN.sub("", topic_v)
        topic_v = topic_v.lower().strip()
        topic_v = WHITESPACE_PATTERN.sub(" ", topic_v)
        return {
            "sentiment": sentiment_v,
            "toxicity": sentiment_v,
            "topic": topic_v,
            "speaker": base
        }
    def process_message(self, index: int, raw: RawMessage) -> PreprocessedMessage:
        """Main processing flow for a single message."""
        content = raw.content
        emojis = self.extract_emojis(content)
        metadata = MessageMetadata(
            emoji_count=len(emojis),
            emoji_list=emojis,
            caps_ratio=self.get_caps_ratio(content),
            repeated_punctuation_count=self.count_repeated_patterns(content, REPEATED_PUNCTUATION_PATTERN),
            repeated_char_count=self.count_repeated_patterns(content, REPEATED_CHARACTER_PATTERN),
            url_count=len(URL_PATTERN.findall(content)),
            has_media=raw.is_media,
            message_length=len(content),
            word_count=len(content.split())
        )
        base_clean = self.clean_base(content)
        variants = self.generate_variants(content, emojis)
        return PreprocessedMessage(
            message_id=index,
            raw=raw,
            base_clean=base_clean,
            variants=variants,
            metadata=metadata
        )
    def process_sequence(self, raw_messages: List[RawMessage]) -> PreprocessingResult:
        """Process a stream of messages and build global metadata."""
        preprocessed = []
        emoji_map = {}
        for i, msg in enumerate(raw_messages):
            processed = self.process_message(i, msg)
            preprocessed.append(processed)
            for emoji in processed.metadata.emoji_list:
                emoji_map[emoji] = emoji_map.get(emoji, 0) + 1
        df = pd.DataFrame([
            {
                "sender": p.raw.sender,
                "msg_len": p.metadata.message_length,
                "caps": p.metadata.caps_ratio,
                "emojis": p.metadata.emoji_count,
                "is_media": p.metadata.has_media
            } for p in preprocessed if p.raw.sender
        ])
        participant_stats = {}
        if not df.empty:
            participant_stats = df.groupby("sender").agg({
                "msg_len": "mean",
                "caps": "mean",
                "emojis": "sum",
                "is_media": "sum"
            }).to_dict(orient="index")
        return PreprocessingResult(
            messages=preprocessed,
            global_metadata={
                "total_emojis": emoji_map,
                "participant_stats": participant_stats
            }
        )
