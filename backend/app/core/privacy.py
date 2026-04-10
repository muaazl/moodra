import gc
import re
from typing import List, Dict, Any, Optional
class PrivacyManager:
    """Handles privacy-related operations like anonymization and memory cleanup."""
    @staticmethod
    def clear_memory():
        """Explicitly trigger garbage collection to reclaim memory from processed chats."""
        gc.collect()
    @staticmethod
    def anonymize_text(text: str, participants: List[str]) -> str:
        """Replace participant names with generic identifiers (e.g., Participant A)."""
        if not participants:
            return text
        mapping = {name: f"Participant {chr(65 + i)}" for i, name in enumerate(participants)}
        sorted_names = sorted(participants, key=len, reverse=True)
        pattern = re.compile("|".join([re.escape(name) for name in sorted_names]))
        def replace(match: re.Match) -> str:
            res = mapping.get(match.group(0), match.group(0))
            return str(res)
        return pattern.sub(replace, text)
    @staticmethod
    def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove potentially sensitive fields from metadata dictionaries."""
        sensitive_keys = {"ip", "user_agent", "session_id", "email"}
        return {k: v for k, v in metadata.items() if k.lower() not in sensitive_keys}
