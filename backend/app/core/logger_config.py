import logging
import re
from typing import Any, Dict

class PrivacyFilter(logging.Filter):
    """Filters sensitive chat patterns from logs."""
    
    # Regex Patterns for potential chat leaks (e.g., [12/03/24, 12:45] Alice: Hello)
    # We catch many WhatsApp formats
    CHAT_PATTERN = re.compile(r'\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}:\d{2}\]?\s+.*?:')

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.msg)
        
        # Redact anything matching chat line signature
        if self.CHAT_PATTERN.search(msg):
            record.msg = self.CHAT_PATTERN.sub("[REDACTED CHAT LINE]:", msg)
            
        # Redact raw strings in message
        if self.CHAT_PATTERN.search(msg):
            record.msg = self.CHAT_PATTERN.sub("[REDACTED CHAT LINE]:", msg)
            
        return True

def setup_privacy_logging(level=logging.INFO):
    """Initializes logging with strict privacy filters."""
    logger = logging.getLogger("uvicorn.access")
    
    # Add Privacy Filter
    privacy_filter = PrivacyFilter()
    logger.addFilter(privacy_filter)
    
    # Basic logging config
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    return logger
