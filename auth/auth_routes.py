from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import User
from schemas.user_schema import UserCreate
from utils.security import verify_password, hash_password
from auth.jwt_handler import create_access_token
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# Fix: was "/auth/login" which caused double prefix → "/auth/auth/login"
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Fix: include user_id and role so get_current_user can read them
    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
