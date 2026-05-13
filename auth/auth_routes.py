from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import User
from schemas.user_schema import TokenResponse, UserCreate, UserResponse
from utils.security import verify_password, hash_password
from auth.jwt_handler import create_access_token
from app.database import get_db
from app.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        logger.warning("AUTH register failed for username=%s", user.username)
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role.value
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("AUTH register success user_id=%s username=%s", new_user.id, new_user.username)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        logger.warning("AUTH login failed for username=%s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role.lower()
    })
    logger.info("AUTH login success user_id=%s username=%s", user.id, user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
