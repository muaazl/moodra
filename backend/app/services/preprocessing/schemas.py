from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..parser.schemas import RawMessage

class MessageMetadata(BaseModel):
    """Features extracted during preprocessing that are useful for downstream analysis."""
    emoji_count: int = 0
    emoji_list: List[str] = Field(default_factory=list)
    caps_ratio: float = 0.0 # Ratio of uppercase letters to total letters
    repeated_punctuation_count: int = 0 # e.g. !!!, ???
    repeated_char_count: int = 0 # e.g. loooooool
    url_count: int = 0
    has_media: bool = False
    message_length: int = 0 # Number of characters (base normalization)
    word_count: int = 0

class PreprocessedMessage(BaseModel):
    """The output of the preprocessing layer."""
    message_id: int # Order in the chat
    raw: RawMessage
    
    # Base normalization: trimmed, standardized whitespace, but preserved case/punctuation
    base_clean: str
    
    # Specific variants for different analysis tasks
    variants: Dict[str, str] = Field(
        default_factory=lambda: {
            "sentiment": "", # Preserved case, punctuation, emojis
            "topic": "",     # Lowercased, no punctuation, maybe no emojis
            "toxicity": "",  # Preserved case/punctuation
            "speaker": ""    # Similar to base_clean
        }
    )
    
    metadata: MessageMetadata
    
class PreprocessingResult(BaseModel):
    """The result of preprocessing a full chat sequence."""
    messages: List[PreprocessedMessage]
    global_metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_emojis": {}, # emoji -> count
            "participant_stats": {} # participant -> metadata averages
        }
    )
