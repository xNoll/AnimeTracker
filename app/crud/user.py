from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password



def get_by_id(db: Session, id: int) -> User | None:
    return db.query(User).filter(User.id == id).first()

def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create(db: Session, data: UserCreate) -> User:
    user = User(
        username = data.username,
        email = data.email,
        hashed_password = hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
