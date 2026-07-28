import re
from rapidfuzz import fuzz

SCAM_PATTERNS = [
    r"crypto\s*giveaway",
    r"t\.me/joinchat",
    r"t\.me/\+",
    r"doubl(e|ing)\s*your\s*(btc|eth|crypto)",
    r"free\s*airdrop",
    r"investment\s*profit",
]

class SpamDetector:
    @staticmethod
    def check_spam(text: str) -> tuple[bool, str]:
        if not text:
            return False, ""

        # 1. Regex check for links & scams
        for pattern in SCAM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, "Scam / Unauthorized Link"

        # 2. Excessive Caps Check (>70% caps if string len > 15)
        if len(text) > 15 and sum(1 for c in text if c.isupper()) / len(text) > 0.70:
            return True, "Excessive Capital Letters"

        # 3. Excessive Emojis
        emoji_count = len(re.findall(r"[\U00010000-\U0010ffff]", text))
        if emoji_count > 12:
            return True, "Excessive Emojis"

        return False, ""
