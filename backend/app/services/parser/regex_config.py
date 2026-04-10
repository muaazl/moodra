import re
TIMESTAMP_START = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[?\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4}[,.]?\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\]?"
)
ANDROID_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\s-\s(.+?):\s(.*)$"
)
ANDROID_SYSTEM_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\s-\s(.+)$"
)
IOS_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\]\s(.+?):\s(.*)$"
)
IOS_SYSTEM_PATTERN = re.compile(
    r"^[\u200c\u200d\u200e\u200f]?\[(\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?)\]\s(.+)$"
)
MEDIA_PLACEHOLDERS = [
    "<Media omitted>",
    "<image omitted>",
    "<video omitted>",
    "<sticker omitted>",
    "<audio omitted>",
    "<document omitted>",
    "GIF omitted",
    "image omitted",
    "video omitted",
    "sticker omitted",
    "audio omitted",
    "document omitted",
]
IS_MEDIA = re.compile(r"<(Media omitted|image|video|sticker|audio|document) omitted>", re.I)