from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.user_model import User
from schemas.user_schema import UserCreate
from utils.security import hash_password
from fastapi import HTTPException
from schemas.user_schema import UserLogin
from utils.security import verify_password
from auth.jwt_handler import create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

# database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create User


@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }


# Get all users
@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# Get user by id
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    # 1. get user
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3. create token
    token = create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id
    })

    # 4. return token
    return {
        "access_token": token,
        "token_type": "bearer"
    }




# Delete user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

