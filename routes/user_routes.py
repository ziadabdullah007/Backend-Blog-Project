from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import logger
from auth.dependencies import get_current_user, require_roles
from models.user_model import User
from schemas.user_schema import MessageResponse, UserCreate, UserResponse, UserUpdate
from utils.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
        role=user.role.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("USER created user_id=%s username=%s", new_user.id, new_user.username)
    return new_user


@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    return db.query(User).order_by(User.id).all()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id and current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user"
        )

    return _get_user_or_404(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = _get_user_or_404(user_id, db)
    is_admin = current_user.role.lower() == "admin"

    if current_user.id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user"
        )

    if user_update.role is not None and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user roles"
        )

    if user_update.username and user_update.username != user.username:
        username_exists = db.query(User).filter(User.username == user_update.username).first()
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_update.username

    if user_update.email and user_update.email != user.email:
        email_exists = db.query(User).filter(User.email == user_update.email).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_update.email

    if user_update.password:
        user.password = hash_password(user_update.password)

    if user_update.role is not None:
        user.role = user_update.role.value

    db.commit()
    db.refresh(user)
    logger.info("USER updated user_id=%s by user_id=%s", user.id, current_user.id)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    user = _get_user_or_404(user_id, db)
    db.delete(user)
    db.commit()
    logger.info("USER deleted user_id=%s by admin_id=%s", user_id, current_user.id)
    return {"message": "User deleted successfully"}