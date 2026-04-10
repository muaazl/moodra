import re
URL_PATTERN = re.compile(r"http[s]?://\S+")
REPEATED_PUNCTUATION_PATTERN = re.compile(r"([!?]{2,})")
REPEATED_CHARACTER_PATTERN = re.compile(r"(.)\1{2,}")
WHITESPACE_PATTERN = re.compile(r"\s+")
ONE_WORD_MESSAGES = ["ok", "k", "sure", "fine", "cool", "done", "lol", "lmao"]
DRY_RESPONSES = ["?", "??", "...", "."]
PUNCTUATION_REMOVAL_PATTERN = re.compile(r'[^\w\s\d]')
