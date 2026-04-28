from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.post_model import Post
from schemas.post_schema import PostCreate

router = APIRouter(prefix="/posts", tags=["Posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/")
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit

    posts = db.query(Post).order_by(Post.id).offset(skip).limit(limit).all()
    total = db.query(Post).count()

    posts_data = []

    for post in posts:
        posts_data.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": posts_data
    }

@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id
    }

@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return {"message": "Post deleted"}