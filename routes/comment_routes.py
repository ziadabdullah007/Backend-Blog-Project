from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db  # ✅ من مكان واحد
from models.comment_model import Comment
from schemas.comment_schema import CommentCreate
from auth.dependencies import get_current_user
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
        post_id=comment.post_id,
        user_id=current_user.id,  
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "id": new_comment.id,
        "content": new_comment.content,
        "post_id": new_comment.post_id,
        "user_id": new_comment.user_id,
        "parent_id": new_comment.parent_id
    }


@router.get("/")
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return [{"id": c.id, "content": c.content, "post_id": c.post_id, "user_id": c.user_id, "parent_id": c.parent_id} for c in comments]


@router.get("/post/{post_id}/nested")
def get_nested_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    comment_dict = {
        c.id: {"id": c.id, "content": c.content, "post_id": c.post_id,
               "user_id": c.user_id, "parent_id": c.parent_id, "replies": []}
        for c in comments
    }

    nested_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in comment_dict:
            comment_dict[c.parent_id]["replies"].append(comment_dict[c.id])
        else:
            nested_comments.append(comment_dict[c.id])

    return nested_comments


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}


