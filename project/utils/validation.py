import re

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))

def not_empty(s: str) -> bool:
    return bool(s and s.strip())
