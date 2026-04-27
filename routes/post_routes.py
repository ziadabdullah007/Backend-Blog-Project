from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.post_model import Post
from schemas.post_schema import PostCreate
from auth.dependencies import get_db, require_roles
from models.user_model import User

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/")
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "author"))
):
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/")
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}