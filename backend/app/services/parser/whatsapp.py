import re
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from .schemas import RawMessage, ParseResult, ParseWarning
from .regex_config import (
    ANDROID_PATTERN,
    ANDROID_SYSTEM_PATTERN,
    IOS_PATTERN,
    IOS_SYSTEM_PATTERN,
    TIMESTAMP_START,
    MEDIA_PLACEHOLDERS
)
logger = logging.getLogger(__name__)
class WhatsAppParser:
    """Orchestrates the conversion of raw WhatsApp text into structured data."""
    def __init__(self):
        self.date_formats = [
            "%d/%m/%Y, %H:%M",
            "%d/%m/%y, %H:%M",
            "%m/%d/%Y, %H:%M",
            "%m/%d/%y, %H:%M",
            "%d/%m/%Y, %H:%M:%S",
            "%d/%m/%y, %H:%M:%S",
            "%d/%m/%y, %I:%M %p",
            "%d/%m/%Y, %I:%M %p",
            "%Y-%m-%d, %H:%M:%S",
            "%Y-%m-%d, %H:%M",
        ]
    def _clean_text(self, text: str) -> str:
        """Removes invisible control characters (LRM, RLM, BOM, etc.)."""
        return text.translate(str.maketrans('', '', '\u200c\u200d\u200e\u200f\ufeff'))
    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Try several common WhatsApp timestamp formats after cleaning."""
        ts_str = self._clean_text(ts_str).strip("[] ")
        for fmt in self.date_formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        return None
    def _is_media(self, content: str) -> bool:
        """Check if message is a media placeholder."""
        return any(placeholder.lower() in content.lower() for placeholder in MEDIA_PLACEHOLDERS)
    def _is_valid_participant(self, sender: str) -> bool:
        """Filter out system messages that got parsed as senders."""
        if not sender: return False
        if len(sender) > 40: return False
        invalid_phrases = [
            " added ", " removed ", " changed the subject", 
            " left", " joined ", " created group", " messages to this group",
            " changed the group", " deleted this group"
        ]
        lower_s = sender.lower()
        if any(p in lower_s for p in invalid_phrases): 
            return False
        return True
    def _is_actually_system_content(self, content: str) -> bool:
        """Checks if content looks like a system notification (e.g. 'User joined')."""
        system_verbs = [
            " joined", " left", " added ", " removed ", " changed the group",
            " changed the subject", " created group", " messages to this group",
            " pinned a message", " deleted a message"
        ]
        lower_c = content.lower()
        if len(content) < 100 and any(v in lower_c for v in system_verbs):
            return True
        return False
    def parse_text(self, text: str) -> ParseResult:
        """Main entry point to parse a block of text."""
        lines = text.splitlines()
        messages: List[RawMessage] = []
        warnings: List[ParseWarning] = []
        current_msg_data: Optional[dict] = None
        participants = set()
        for i, line in enumerate(lines, 1):
            line = self._clean_text(line).strip()
            if not line:
                continue
            if TIMESTAMP_START.match(line):
                if current_msg_data:
                    messages.append(self._to_raw_message(current_msg_data))
                extracted = self._extract_message_parts(line)
                if extracted:
                    ts_str, sender, content, is_system = extracted
                    dt = self._parse_timestamp(ts_str)
                    if dt:
                        is_actually_system = is_system or not self._is_valid_participant(sender) or self._is_actually_system_content(content)
                        current_msg_data = {
                            "timestamp": dt,
                            "sender": sender if not is_actually_system else None,
                            "content": content,
                            "is_system": is_actually_system
                        }
                        if current_msg_data["sender"]:
                            participants.add(current_msg_data["sender"])
                    else:
                        warnings.append(ParseWarning(line_number=i, content=line, reason="Invalid date format"))
                else:
                    warnings.append(ParseWarning(line_number=i, content=line, reason="Unrecognizable message structure"))
            else:
                if current_msg_data:
                    current_msg_data["content"] += "\n" + line
                else:
                    warnings.append(ParseWarning(line_number=i, content=line, reason="Line orphaned (no parent message)"))
        if current_msg_data:
            messages.append(self._to_raw_message(current_msg_data))
        metadata = {
            "participants": list(participants),
            "message_count": len(messages),
            "date_range": {
                "start": messages[0].timestamp if messages else None,
                "end": messages[-1].timestamp if messages else None
            }
        }
        return ParseResult(messages=messages, warnings=warnings, metadata=metadata)
    def _extract_message_parts(self, line: str) -> Optional[Tuple[str, Optional[str], str, bool]]:
        """Identify which regex matches the line and return (timestamp, sender, content, is_system)."""
        match = ANDROID_PATTERN.match(line)
        if match:
            return match.group(1), match.group(2), match.group(3), False
        match = IOS_PATTERN.match(line)
        if match:
            return match.group(1), match.group(2), match.group(3), False
        match = ANDROID_SYSTEM_PATTERN.match(line)
        if match:
            return match.group(1), None, match.group(2), True
        match = IOS_SYSTEM_PATTERN.match(line)
        if match:
            return match.group(1), None, match.group(2), True
        return None
    def _to_raw_message(self, data: dict) -> RawMessage:
        """Convert dict buffer to a RawMessage object."""
        return RawMessage(
            timestamp=data["timestamp"],
            sender=data.get("sender"),
            content=data["content"],
            is_system=data["is_system"],
            is_media=self._is_media(data["content"])
        )
