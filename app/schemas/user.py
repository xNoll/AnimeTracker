from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request schemas (what the client sends) ──────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, _ and -")
        return v.lower()


class UserLogin(BaseModel):
    username: str
    password: str


# ── Response schemas (what the API returns — never expose hashed_password) ───

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # allows creating from ORM objects


# ── Auth ─────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
