import logging
import re
from typing import Any, Dict
class PrivacyFilter(logging.Filter):
    """Filters sensitive chat patterns from logs."""
    CHAT_PATTERN = re.compile(r'\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}:\d{2}\]?\s+.*?:')
    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.msg)
        if self.CHAT_PATTERN.search(msg):
            record.msg = self.CHAT_PATTERN.sub("[REDACTED CHAT LINE]:", msg)
        if self.CHAT_PATTERN.search(msg):
            record.msg = self.CHAT_PATTERN.sub("[REDACTED CHAT LINE]:", msg)
        return True
def setup_privacy_logging(level=logging.INFO):
    """Initializes logging with strict privacy filters."""
    logger = logging.getLogger("uvicorn.access")
    privacy_filter = PrivacyFilter()
    logger.addFilter(privacy_filter)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logger
