from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

# Tells FastAPI where the login endpoint is (used in /docs Authorize button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency injected into any route that requires authentication.
    Usage:  current_user: User = Depends(get_current_user)
    """
    credentials_error = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials.",
        headers = {"WWW-Authenticate": "Bearer"}
    )
    payload = decode_access_token(token)
    if not payload:
        raise credentials_error
    
    username: str | None = payload.get("sub")
    if not username:
        raise credentials_error
    
    user = crud.user.get_by_username(db, username)
    if not user or not user.is_active:
        raise credentials_error
    
    return user