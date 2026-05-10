import bcrypt
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings



# ── Passwords ────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# JWT
def create_access_token_data(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes= settings.access_token_expire_minutes
    )
    payload.update({"exp": expire})

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    

def decode_access_token(token: str) -> dict | None:
    """Returns the decoded payload or None if the token is invalid/expired."""
    try:
        return jwt.decode(token=token, key=settings.secret_key, algorithms=settings.algorithm)
    except JWTError:
        return None
    
