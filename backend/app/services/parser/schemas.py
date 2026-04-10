from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
class RawMessage(BaseModel):
    """Normalized message format for internal processing."""
    timestamp: datetime
    sender: Optional[str] = Field(None, description="The message sender. None for system messages.")
    content: str
    is_system: bool = Field(False, description="Flag for automated system messages (e.g. encryption/joined labels).")
    is_media: bool = Field(False, description="Flag for media placeholders like <Media omitted>.")
class ParseWarning(BaseModel):
    """Soft errors encountered during parsing."""
    line_number: int
    content: str
    reason: str
class ParseResult(BaseModel):
    """The final structured output of the parsing operation."""
    messages: List[RawMessage]
    warnings: List[ParseWarning]
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "participants": [],
            "message_count": 0,
            "date_range": {"start": None, "end": None}
        }
    )
