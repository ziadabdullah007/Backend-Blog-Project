import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logger import logger
from app.redis_client import cache_delete_pattern, cache_get, cache_setex
from auth.dependencies import get_current_user, require_roles
from models.post_model import Post
from models.user_model import User
from schemas.post_schema import (
    PaginatedPostsResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from schemas.user_schema import MessageResponse

router = APIRouter(prefix="/posts", tags=["Posts"])


def clear_posts_cache():
    cache_delete_pattern("posts:*")
    cache_delete_pattern("post:*")


def _get_post_or_404(post_id: int, db: Session) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def _ensure_post_owner_or_admin(post: Post, current_user: User) -> None:
    if post.user_id != current_user.id and current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to modify this post")


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
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

    clear_posts_cache()
    logger.info(f"POST /posts created post id={new_post.id}")
    return new_post


@router.get("/", response_model=PaginatedPostsResponse)
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


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    cache_key = f"post:{post_id}"
    cached_post = cache_get(cache_key)
    if cached_post:
        return json.loads(cached_post)

    post = _get_post_or_404(post_id, db)
    post_data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id
    }
    cache_setex(cache_key, 60, json.dumps(post_data))
    return post_data


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = _get_post_or_404(post_id, db)
    _ensure_post_owner_or_admin(post, current_user)

    if post_update.title is None and post_update.content is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to update a post"
        )

    if post_update.title is not None:
        post.title = post_update.title

    if post_update.content is not None:
        post.content = post_update.content

    db.commit()
    db.refresh(post)
    clear_posts_cache()
    logger.info("PUT /posts/%s updated by user_id=%s", post.id, current_user.id)
    return post


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = _get_post_or_404(post_id, db)
    _ensure_post_owner_or_admin(post, current_user)

    db.delete(post)
    db.commit()
    clear_posts_cache()
    logger.info("DELETE /posts/%s deleted by user_id=%s", post_id, current_user.id)
    return {"message": "Post deleted"}