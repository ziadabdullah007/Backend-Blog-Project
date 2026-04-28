from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.comment_model import Comment
from schemas.comment_schema import CommentCreate

router = APIRouter(prefix="/comments", tags=["Comments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create comment
@router.post("/")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = Comment(
        content=comment.content,
        post_id=comment.post_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Get all comments
@router.get("/")
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments


# Delete comment
@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}