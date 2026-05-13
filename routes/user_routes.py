from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db  
from models.user_model import User
from schemas.user_schema import UserCreate
from utils.security import hash_password, verify_password
from auth.jwt_handler import create_access_token
from auth.dependencies import get_current_user, require_roles  # ✅ للحماية

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role}


@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))  # ✅ admins بس
):
    return db.query(User).all()


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))  # ✅ محمي دلوقتي
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}