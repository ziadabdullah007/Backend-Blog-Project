from fastapi import APIRouter, Depends, HTTPException
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

@router.post("/")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = Comment(
        content=comment.content,
        post_id=comment.post_id,
        user_id=1,
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

    return [
        {
            "id": c.id,
            "content": c.content,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "parent_id": c.parent_id
        }
        for c in comments
    ]

@router.get("/post/{post_id}/nested")
def get_nested_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    comment_dict = {
        c.id: {
            "id": c.id,
            "content": c.content,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "parent_id": c.parent_id,
            "replies": []
        }
        for c in comments
    }

    nested_comments = []

    for c in comments:
        if c.parent_id:
            parent = comment_dict.get(c.parent_id)
            if parent:
                parent["replies"].append(comment_dict[c.id])
        else:
            nested_comments.append(comment_dict[c.id])

    return nested_comments

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}




