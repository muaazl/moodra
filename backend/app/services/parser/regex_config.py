import re

# To check if a line starts with a timestamp
# We allow optional control characters like LRM/RLM that often appear in WhatsApp exports
TIMESTAMP_START = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[?\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4}[,.]?\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\]?"
)

# User Message: 27/12/2023, 10:45 - Sender: Message
ANDROID_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\s-\s(.+?):\s(.*)$"
)

# System Message: 27/12/2023, 10:45 - Messages you send...
ANDROID_SYSTEM_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\s-\s(.+)$"
)

# User Message: [27/12/23, 10:45:30] Sender: Message
IOS_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\]\s(.+?):\s(.*)$"
)

# System Message: [27/12/23, 10:45:30] Sender created group...
IOS_SYSTEM_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\]\s(.+)$"
)

# Common media placeholders in WhatsApp exports
MEDIA_PLACEHOLDERS = [
    "<Media omitted>",
    "<image omitted>",
    "<video omitted>",
    "<sticker omitted>",
    "<audio omitted>",
    "<document omitted>",
    "GIF omitted",  # Android
    "image omitted", # Android
    "video omitted", # Android
    "sticker omitted", # Android
    "audio omitted", # Android
    "document omitted", # Android
]

# Regex for checking media specifically
IS_MEDIA = re.compile(r"<(Media omitted|image|video|sticker|audio|document) omitted>", re.I)