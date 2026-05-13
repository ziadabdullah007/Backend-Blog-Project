from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import logger
from auth.dependencies import get_current_user
from models.comment_model import Comment
from models.post_model import Post
from models.user_model import User
from schemas.comment_schema import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    PaginatedCommentsResponse,
)
from schemas.user_schema import MessageResponse

router = APIRouter(prefix="/comments", tags=["Comments"])


def _get_comment_or_404(comment_id: int, db: Session) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


def _serialize_comment(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "parent_id": comment.parent_id,
        "replies": [],
    }


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment.parent_id is not None:
        parent_comment = db.query(Comment).filter(Comment.id == comment.parent_id).first()
        if parent_comment is None:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent_comment.post_id != comment.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment must belong to the same post"
            )

    new_comment = Comment(
        content=comment.content,
        post_id=comment.post_id,
        user_id=current_user.id,  
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    logger.info("POST /comments created comment_id=%s by user_id=%s", new_comment.id, current_user.id)
    return _serialize_comment(new_comment)


@router.get("/", response_model=PaginatedCommentsResponse)
def get_comments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    comments = db.query(Comment).order_by(Comment.id).offset(skip).limit(limit).all()
    total = db.query(Comment).count()
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": [_serialize_comment(comment) for comment in comments],
    }


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = _get_comment_or_404(comment_id, db)
    return _serialize_comment(comment)


@router.get("/post/{post_id}/nested", response_model=list[CommentResponse])
def get_nested_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    comment_dict = {c.id: _serialize_comment(c) for c in comments}

    nested_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in comment_dict:
            comment_dict[c.parent_id]["replies"].append(comment_dict[c.id])
        else:
            nested_comments.append(comment_dict[c.id])

    return nested_comments


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = _get_comment_or_404(comment_id, db)
    if comment.user_id != current_user.id and current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to update this comment")

    comment.content = comment_update.content
    db.commit()
    db.refresh(comment)
    logger.info("PUT /comments/%s updated by user_id=%s", comment.id, current_user.id)
    return _serialize_comment(comment)


@router.delete("/{comment_id}", response_model=MessageResponse)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    comment = _get_comment_or_404(comment_id, db)

    if comment.user_id != current_user.id and current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")

    db.delete(comment)
    db.commit()
    logger.info("DELETE /comments/%s deleted by user_id=%s", comment_id, current_user.id)
    return {"message": "Comment deleted"}


