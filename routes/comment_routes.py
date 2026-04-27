from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.comment_model import Comment
from schemas.comment_schema import CommentCreate
from auth.dependencies import get_db, require_roles, get_current_user
from models.user_model import User

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/")
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_comment = Comment(
        content=comment.content,
        post_id=comment.post_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/")
def get_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}