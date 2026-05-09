import bcrypt
from datetime import datetime, timedelta, timezone



# ── Passwords ────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
