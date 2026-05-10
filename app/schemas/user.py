from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# Request schema - what the user sends.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=100)
    email: EmailStr

    @field_validator
    @classmethod
    def check_username_alpahnum(cls, user: str) -> str:
        if not user.replace("_","").replace("-","").isalnum:
            raise ValueError("Username can only contain letter, numbers, dashes('-') and underscore('_').")
        
        return user.lower()
    

# Response schema - what the API sends.
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}    # allows creating from ORM objects