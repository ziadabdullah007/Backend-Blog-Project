from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db  
from models.post_model import Post
from schemas.post_schema import PostCreate
from app.redis_client import cache_delete_pattern, cache_get, cache_setex
from app.logger import logger
from auth.dependencies import get_current_user
from models.user_model import User
import json

router = APIRouter(prefix="/posts", tags=["Posts"])


def clear_posts_cache():
    cache_delete_pattern("posts:*")


@router.post("/")
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ lazim تكون logged in
):
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id  # ✅ من الـ token مش من الـ body
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    clear_posts_cache()
    logger.info(f"POST /posts created post id={new_post.id}")

    return {"id": new_post.id, "title": new_post.title, "content": new_post.content, "user_id": new_post.user_id}


@router.get("/")
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    cache_key = f"posts:page={page}:limit={limit}"
    cached_posts = cache_get(cache_key)
    if cached_posts:
        return json.loads(cached_posts)

    skip = (page - 1) * limit
    posts = db.query(Post).order_by(Post.id).offset(skip).limit(limit).all()
    total = db.query(Post).count()

    posts_data = [{"id": p.id, "title": p.title, "content": p.content, "user_id": p.user_id} for p in posts]
    response = {"page": page, "limit": limit, "total": total, "data": posts_data}

    cache_setex(cache_key, 60, json.dumps(response))
    return response


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": post.id, "title": post.title, "content": post.content, "user_id": post.user_id}


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ lazim تكون logged in
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to delete this post")

    db.delete(post)
    db.commit()
    clear_posts_cache()
    return {"message": "Post deleted"}