from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..parser.schemas import RawMessage
class MessageMetadata(BaseModel):
    """Features extracted during preprocessing that are useful for downstream analysis."""
    emoji_count: int = 0
    emoji_list: List[str] = Field(default_factory=list)
    caps_ratio: float = 0.0
    repeated_punctuation_count: int = 0
    repeated_char_count: int = 0
    url_count: int = 0
    has_media: bool = False
    message_length: int = 0
    word_count: int = 0
class PreprocessedMessage(BaseModel):
    """The output of the preprocessing layer."""
    message_id: int
    raw: RawMessage
    base_clean: str
    variants: Dict[str, str] = Field(
        default_factory=lambda: {
            "sentiment": "",
            "topic": "",
            "toxicity": "",
            "speaker": ""
        }
    )
    metadata: MessageMetadata
class PreprocessingResult(BaseModel):
    """The result of preprocessing a full chat sequence."""
    messages: List[PreprocessedMessage]
    global_metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_emojis": {},
            "participant_stats": {}
        }
    )
