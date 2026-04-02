import re

# To avoid over-cleaning, focus on identifying signals
URL_PATTERN = re.compile(r"http[s]?://\S+") # Basic URL
REPEATED_PUNCTUATION_PATTERN = re.compile(r"([!?]{2,})") # ??, !!, ?!
REPEATED_CHARACTER_PATTERN = re.compile(r"(.)\1{2,}") # looooool, wowwww
WHITESPACE_PATTERN = re.compile(r"\s+") # Standardize spaces

# Signals for tension/dryness
ONE_WORD_MESSAGES = ["ok", "k", "sure", "fine", "cool", "done", "lol", "lmao"]
DRY_RESPONSES = ["?", "??", "...", "."] # Single dots or question marks

# For variants
PUNCTUATION_REMOVAL_PATTERN = re.compile(r'[^\w\s\d]') # Not alphanumeric or whitespace
